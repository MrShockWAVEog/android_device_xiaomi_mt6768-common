#!/usr/bin/env python3
"""Check the ROM camera payload and evaluate its Make rules without a ROM build.

Run from anywhere. --desktop-layout supports the separate repository checkouts
used during integration; otherwise use the standard device/xiaomi + vendor/xiaomi
layout. This does not compile Android or test a camera HAL.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess
import tempfile
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--desktop-layout', action='store_true')
    args = parser.parse_args()
    common = Path(__file__).resolve().parents[1]
    root = common.parent
    prebuilt = common / 'prebuilt/LeicaCameraMT6768'
    provenance = json.loads((prebuilt / 'provenance.json').read_text())
    patch = runpy.run_path(str(common / 'camera/patch_vendor.py'))['patch']
    checks = []

    def check(condition, message):
        if not condition:
            raise ValueError(message)
        checks.append(message)

    for line in (prebuilt / 'SHA256SUMS').read_text().splitlines():
        digest, name = line.split('  ', 1)
        check(hashlib.sha256((prebuilt / name).read_bytes()).hexdigest() == digest,
              f'Imported file hash: {name}')
        check(provenance['files'][name] == digest, f'Provenance hash: {name}')
    native_names = sorted(path.name for path in (prebuilt / 'lib/arm64').glob('*.so'))
    check(len(native_names) == 32, 'All 32 app-private JNI inputs present')
    for name in native_names:
        header = (prebuilt / 'lib/arm64' / name).read_bytes()[:20]
        check(header[:6] == b'\x7fELF\x02\x01' and header[18:20] == b'\xb7\x00',
              f'ARM64 JNI: {name}')

    # Evaluate the real Android.mk; stub only Android's module-registration layer.
    with tempfile.TemporaryDirectory(prefix='leica-rom-make-') as temporary:
        temp = Path(temporary)
        records = temp / 'records'
        clear = temp / 'clear.mk'
        clear.write_text('$(foreach v,$(filter-out LOCAL_PATH,$(filter LOCAL_%,$(.VARIABLES))),$(eval $(v) :=))\n')
        register = temp / 'register.mk'
        fields = ['LOCAL_MODULE', 'LOCAL_SRC_FILES', 'LOCAL_MODULE_CLASS',
                  'LOCAL_MODULE_PATH', 'LOCAL_MODULE_STEM', 'LOCAL_MODULE_SUFFIX',
                  'LOCAL_REQUIRED_MODULES', 'LOCAL_OVERRIDES_PACKAGES',
                  'LOCAL_REPLACE_PREBUILT_APK_INSTALLED', 'LOCAL_CERTIFICATE',
                  'LOCAL_INSTALLED_MODULE_STEM', 'LOCAL_IS_RUNTIME_RESOURCE_OVERLAY',
                  'LOCAL_STRIP_MODULE']
        register.write_text('$(file >>' + str(records) + ',' + '|'.join('$(' + field + ')' for field in fields) + ')\n')
        makefile = temp / 'Makefile'
        makefile.write_text(f'''my-dir = {prebuilt}
CLEAR_VARS := {clear}
BUILD_PREBUILT := {register}
TARGET_DEVICE ?= merlinx
TARGET_OUT_APPS_PRIVILEGED := /system/priv-app
TARGET_OUT_PRODUCT := /product
TARGET_OUT_ETC := /system/etc
include {prebuilt / 'Android.mk'}
all:
\t@:
''')
        for device in ['merlinx', 'merlin', 'merlinnfc', 'lancelot', 'galahad', 'unsupported']:
            records.write_text('')
            subprocess.run(['make', '--no-print-directory', '-f', str(makefile),
                            f'TARGET_DEVICE={device}'], check=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True)
            rows = [dict(zip(fields, line.split('|'))) for line in records.read_text().splitlines()]
            if device == 'unsupported':
                check(not rows, 'No camera modules registered for unsupported devices')
                continue
            modules = {row['LOCAL_MODULE']: row for row in rows}
            check(len(modules) == len(rows) == 36, f'{device}: 36 unique camera build modules')
            camera = modules['LeicaCameraMT6768']
            check(set(camera['LOCAL_REQUIRED_MODULES'].split()) == set(modules) - {'LeicaCameraMT6768'},
                  f'{device}: every runtime dependency selected by the app')
            check('Aperture' in camera['LOCAL_OVERRIDES_PACKAGES'].split(), f'{device}: Aperture overridden')
            outputs = set()
            for name, row in modules.items():
                check((prebuilt / row['LOCAL_SRC_FILES']).is_file(), f'{device}: input exists for {name}')
                directory = row['LOCAL_MODULE_PATH']
                if row['LOCAL_MODULE_CLASS'] == 'APPS' and row['LOCAL_IS_RUNTIME_RESOURCE_OVERLAY'] != 'true':
                    directory += '/' + name
                stem = row['LOCAL_INSTALLED_MODULE_STEM'] or row['LOCAL_MODULE_STEM'] or name
                if not row['LOCAL_INSTALLED_MODULE_STEM']:
                    stem += row['LOCAL_MODULE_SUFFIX']
                installed = directory + '/' + stem
                check(installed not in outputs, f'{device}: unique output {installed}')
                outputs.add(installed)
                if row['LOCAL_MODULE_CLASS'] == 'SHARED_LIBRARIES':
                    check(directory == '/system/priv-app/LeicaCameraMT6768/lib/arm64',
                          f'{device}: app-private JNI path for {name}')
                    check(row['LOCAL_STRIP_MODULE'] == 'false', f'{device}: JNI kept unchanged for {name}')
                elif row['LOCAL_MODULE_CLASS'] == 'APPS':
                    check(row['LOCAL_CERTIFICATE'] == 'PRESIGNED' and
                          Path(row['LOCAL_REPLACE_PREBUILT_APK_INSTALLED']).is_file(),
                          f'{device}: signed APK copied unchanged for {name}')
            check('/system/priv-app/LeicaCameraMT6768/LeicaCamera.apk' in outputs,
                  f'{device}: exact tested APK install path')
            check('/product/overlay/LeicaCameraMT6768Overlay.apk' in outputs,
                  f'{device}: defaults overlay install path')

    contexts = []
    for line in (common / 'sepolicy/vendor/file_contexts').read_text().splitlines():
        if line.strip() and not line.startswith('#'):
            pattern, context = line.split()
            contexts.append((pattern, context))
    for path in ['/data/vendor/camera', '/data/vendor/camera/merlin_goldResult.bin',
                 '/data/vendor/camera/rear_dc_cal_wd.bin', '/data/vendor/camera/model',
                 '/data/vendor/camera/model/rt_model/mask/cache_data']:
        check([context for pattern, context in contexts if re.fullmatch(pattern, path)] ==
              ['u:object_r:persist_camera_data_file:s0'], f'Camera-private context: {path}')
    check(not any(re.fullmatch(pattern, '/data/vendor/camera/unrelated.log')
                  for pattern, _ in contexts), 'Label changes limited to tested calibration/model paths')
    for device, family in [('merlinx', 'merlin'), ('lancelot', 'lancelot')]:
        tree = root / (f'android_device_xiaomi_{device}' if args.desktop_layout else device)
        vendor = (root / f'proprietary_vendor_xiaomi_{device}' if args.desktop_layout else
                  root.parents[1] / 'vendor/xiaomi' / device)
        product = (tree / 'device.mk').read_text()
        check(f'ApertureOverlay{device.capitalize()}' not in product,
              f'{device}: Aperture overlay not selected')
        init = (tree / 'rootdir/etc/init.project.rc').read_text()
        check(init.index('restorecon_recursive /data/vendor/camera') >
              init.index('copy /vendor/etc/camera/model/bokeh_model/segment_model'),
              f'{device}: restorecon runs after model/calibration copies')
        extract = tree / 'extract-files.py'
        parsed = ast.parse(extract.read_text())
        callback = next(node for node in parsed.body if isinstance(node, ast.FunctionDef)
                        and node.name == 'blob_fixup_leica_camera')
        with tempfile.TemporaryDirectory(prefix='leica-rom-extract-') as temporary:
            temp = Path(temporary)
            (temp / 'mt6768-common').symlink_to(common, target_is_directory=True)
            (temp / device).mkdir()
            script = temp / device / 'extract-files.py'
            script.touch()
            namespace = {'Path': Path, 'runpy': runpy, '__file__': str(script)}
            exec(compile(ast.Module(body=[callback], type_ignores=[]), str(extract), 'exec'), namespace)
            for name in ['libmibokeh_mt6768.so', 'libarcsoft_supernight.so']:
                relative = 'proprietary/vendor/lib64/' + name
                data = (vendor / relative).read_bytes()
                expected = provenance['files'][f'vendor/{device}/{name}']
                check(hashlib.sha256(data).hexdigest() == expected, f'{device}: patched vendor hash {name}')
                check(patch(data, name, family) == data, f'{device}: idempotent {name}')
                original = subprocess.run(['git', 'show', f'HEAD:{relative}'], cwd=vendor,
                                          check=True, stdout=subprocess.PIPE).stdout
                check(patch(original, name, family) == data, f'{device}: reproducible stock patch {name}')
                test_file = temp / name
                test_file.write_bytes(original)
                namespace['blob_fixup_leica_camera'](None, None, str(test_file))
                check(test_file.read_bytes() == data, f'{device}: extraction callback produces {name}')
                try:
                    patch(b'unknown vendor variant', name, family)
                except ValueError:
                    check(True, f'{device}: unknown {name} rejected')
                else:
                    raise ValueError('Unknown blob accepted')
        check('vendor/lib64/libmibokeh_mt6768.so' in extract.read_text() and
              'vendor/lib64/libarcsoft_supernight.so' in extract.read_text(),
              f'{device}: both engine fixups registered')
    resources = ET.parse(common / 'overlay-lineage/lineage-sdk/lineage/res/res/values/config.xml')
    allowed = resources.find(".//string-array[@name='config_cameraAuxPackageAllowList']")
    check([item.text for item in allowed] == ['com.android.camera'], 'Leica has auxiliary camera access')
    check('LeicaCameraMT6768' in (common / 'mt6768.mk').read_text(), 'Common product selects Leica')
    print(json.dumps({'result': 'pass', 'checks': len(checks),
                      'scope': 'Payload hashes, Make module registration, install paths, extraction patches, policy paths; no full Android build or hardware tests.'}, indent=2))


if __name__ == '__main__':
    main()
