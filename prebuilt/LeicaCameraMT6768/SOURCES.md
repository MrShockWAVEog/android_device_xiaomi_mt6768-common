# Leica Camera for MT6768 — ROM integration

Module release: 1.0.1, author/maintainer: MrShockWAVEog.

Camera port: ItzDFPlayer, Universal Leica 5.0 Beta 8.3 (599830000).
Source: https://gitlab.com/ItzDFPlayer/vendor_xiaomi_miuicamera
Pinned commit: e39a100a25abe6c026a8ea78f3812019f38ad33c.

The imported payload is byte-identical to Leica-mt6768-v1.0.1-stable.zip,
SHA256 bd34d27d9d7d743f0093471ff397a5cdead2fefc2a5c1cbb3d92038a0ee2f5cc.
`SHA256SUMS` covers all local APK/config/JNI inputs; `provenance.json` also records
the two device-specific patched vendor engines. Private signing keys and user
photos/logs are not included.

## Build layout

- `/system/priv-app/LeicaCameraMT6768/LeicaCamera.apk`: signed camera APK.
- `/system/priv-app/LeicaCameraMT6768/lib/arm64/`: 32 private JNI libraries.
- `/product/overlay/LeicaCameraMT6768Overlay.apk`: signed defaults overlay.
- `/system/etc/permissions/privapp-permissions-leica-mt6768.xml`.
- `/system/etc/sysconfig/leica-mt6768-hiddenapi.xml`.
- `/vendor/lib64/libmibokeh_mt6768.so`: existing vendor module, patched in place.
- `/vendor/lib64/libarcsoft_supernight.so`: existing vendor module, patched with
  the appropriate device-family variant.

Android.mk uses `PRESIGNED` and `LOCAL_REPLACE_PREBUILT_APK_INSTALLED` to preserve
the tested APKs and signing identity. The camera has compressed DEX entries;
repacking a signed APK would invalidate its v2/v3 signature. DEX preoptimization
is disabled. App-private JNI uses distinct build module names and explicit
private install paths, preserving the release files without installing copies
over system-wide libraries. The stock vendor prebuilt definitions already
preserve both patched engines without stripping.

The build's package override removes Aperture even if Infinity selects it later
in product inheritance. Both device products omit their Aperture overlays.
The common lineage auxiliary-camera allowlist selects `com.android.camera`.

The native patches preserve the original vendor ABI. Front Portrait selects the
existing CPU segmenter; Night narrows eight out-of-bounds SIMD loads while
preserving their consumed operands. Rear Portrait's camera-ID 61 request hook is
already in the signed APK. Permanent file-context rules label the camera-data
directory, its .bin calibration copies and model tree with the existing
`persist_camera_data_file` type. Device init restores these labels after copying
the files, including on dirty upgrades. Existing camera-provider policy grants
access; no permissive domains, new broad allows, factory calibration changes or
module boot scripts are added.

## Validation scope

The imported module payload was hardware-tested on Merlinx, Infinity X 4.2,
Android 17, kernel 4.19. The built-in ROM variant still requires a complete ROM
build/flash and camera tests. Lancelot and Android 13–16 have not been tested on
hardware. The APK's minimum SDK is 29 and target SDK 33; that alone does not
establish compatibility with every ROM/vendor stack.

The standalone KernelSU module and release ZIP are separate artifacts; installing
one is unnecessary for this ROM integration. Disable/uninstall an older module
before validating the built-in camera.

Android prebuilt APK handling reference:
https://android.googlesource.com/platform/build/+/refs/heads/main/core/app_prebuilt_internal.mk

Local integration checks passed on 14 November 2026 using
`python3 camera/verify_integration.py --desktop-layout`: imported hashes, ARM64
JNI headers, real Android.mk evaluation with a stub module-registration layer,
dependency selection, exact install paths, both extraction callbacks, stock-to-
patched engine reproduction, unknown-blob rejection and camera-data context
matching. XML/Python syntax and `git diff --check` also passed. These checks do
not run Soong/Kati, compile SELinux policy or build/flash a ROM. In a standard
Android checkout, omit `--desktop-layout`; the stock-reproduction check uses
the vendor repositories' committed blobs as its baseline.
