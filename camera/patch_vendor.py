#!/usr/bin/env python3
"""Reproduce the hash-guarded Leica MT6768 v1.0.1 native fixes.

Accept the inspected stock blob or the exact already-patched output only.
Unknown variants must be reviewed instead of patching an arbitrary instruction.
"""
import argparse
import hashlib
from pathlib import Path
import struct

BOKEH_SOURCE = '70c6abe8ee6df43570a620be9436ef796893f56c4eebacc7b737446bc53458b3'
BOKEH_OUTPUT = '9c3047a5f562ae429a59ea9cff57cb8e0463975ebc043bf600ab7cede3a8db00'
NIGHT = {
    'merlin': (
        '313341d314ff508895fce5bb20b73a209cc7412b89aa390bbd63079a8f828318',
        'e0ac78474267d296eeca2e93feb4b6e5cef9ee672efd15ca1c39e7badbac00e7',
        0x1294a0,
    ),
    'lancelot': (
        '3959acab9fcdf22b8c6561771ad07d536dd52bcc89f3dc46d6aec6d8d2bcf44e',
        '8e7bae18964fd2772dd1703f287131fc77fac7cb34ae46747d6051e0b32bf93f',
        0x141cb0,
    ),
}
NIGHT_LOADS = [
    (0x04, '71f15ffc'), (0x0c, '721140fc'), (0x14, '73f15ffc'),
    (0x18, '740140fd'), (0x28, '711140fc'), (0x40, '72f15ffc'),
    (0x50, '730140fd'), (0x5c, '741140fc'),
]


def patch(data, name, family):
    if family not in NIGHT:
        raise ValueError(f'Unsupported family: {family}')
    if name == 'libmibokeh_mt6768.so':
        source, output = BOKEH_SOURCE, BOKEH_OUTPUT
        replacements = [(0xb0ed0, bytes.fromhex('f303002a'), bytes.fromhex('f3031f2a'))]
    elif name == 'libarcsoft_supernight.so':
        source, output, start = NIGHT[family]
        replacements = []
        for relative, instruction in NIGHT_LOADS:
            before = bytes.fromhex(instruction)
            after = struct.pack('<I', struct.unpack('<I', before)[0] & ~0x40000000)
            replacements.append((start + relative, before, after))
    else:
        raise ValueError(f'Unsupported camera blob: {name}')
    digest = hashlib.sha256(data).hexdigest()
    if digest == output:
        return data
    if digest != source:
        raise ValueError(f'Unsupported {family} {name}: {digest}')
    result = bytearray(data)
    for offset, before, after in replacements:
        if data[offset:offset + len(before)] != before:
            raise ValueError(f'Unexpected instruction in {name} at {offset:#x}')
        result[offset:offset + len(before)] = after
    result = bytes(result)
    if hashlib.sha256(result).hexdigest() != output:
        raise ValueError(f'Patched hash mismatch: {name}')
    return result


def patch_file(file_path, family):
    path = Path(file_path)
    original = path.read_bytes()
    result = patch(original, path.name, family)
    if result != original:
        path.write_bytes(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', type=Path)
    parser.add_argument('--family', required=True, choices=tuple(NIGHT))
    args = parser.parse_args()
    patch_file(args.file, args.family)
