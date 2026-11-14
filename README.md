# Common device tree for Xiaomi MT6768 devices

## Leica Camera

Leica Camera for MT6768 **1.0.1**, maintained by **MrShockWAVEog**, replaces
LineageOS Aperture in the Merlinx and Lancelot Infinity builds. The common product
selects `LeicaCameraMT6768`, which overrides `Aperture`; the device products no
longer select the Aperture overlays. The auxiliary-camera allowlist now includes
`com.android.camera`.

The signed APK, app-private ARM64 JNI, defaults overlay, privileged permissions
and hidden-API allowlist are bundled under `prebuilt/LeicaCameraMT6768`. Both vendor
trees include the matching Portrait CPU and ArcSoft Night patches. Device
extraction callbacks reapply the hash-guarded patches from `camera/patch_vendor.py`
and reject unknown blob variants. Camera-data file contexts and device init
restorecon replace the KernelSU module's boot-time label repair. No root or
module mount provider is needed for the ROM camera.

All five repositories must be used together: the common device tree, both device
trees and the two corresponding vendor trees. For one device, use the common
tree plus that device's device/vendor trees. Keep their usual Android source
paths (`device/xiaomi/mt6768-common`, `device/xiaomi/merlinx` or `lancelot`, and
`vendor/xiaomi/merlinx` or `lancelot`). APKs and app-private JNI use Git LFS;
install Git LFS before committing or checking out this tree, and materialize
them with `git lfs pull` in the common tree before building.

See `prebuilt/LeicaCameraMT6768/SOURCES.md` for hashes, build behavior and limits.
Full ROM compilation and testing of the built-in app on a flashed ROM remain
required; local checks do not establish a successful ROM build. Merlinx Android
17 has hardware validation of the identical module payload; Lancelot and
Android 13–16 remain untested. Disable/uninstall the old `leica_mt6768` KernelSU
module before testing a ROM with this built-in camera to avoid stale overlays.

## ViPER4Android

This tree bundles [ViPER4Android 2.1.2](https://github.com/likelikeslike/ViPER4Android/releases/tag/2.1.2)
and the ARM/ARM64 drivers from [ViPER4Android RE 2.1.2](https://github.com/likelikeslike/ViPERFX_RE/releases/tag/v2.1.2)
in `prebuilt/ViPER4Android`. No external app project or Magisk module is required.
Remove the old `TogoFire/packages_apps_ViPER4AndroidFX` entry from your local
manifest and its checkout at `packages/apps/ViPER4AndroidFX` before building
to avoid duplicate driver module definitions.

The upstream-signed app installs in system_ext with the privileged
`MODIFY_AUDIO_ROUTING` permission. Both driver ABIs install in vendor's
`lib/soundfx` and `lib64/soundfx` directories. The vendor audio effects
configuration registers `libv4a_re.so` for the device's HIDL audio HAL;
`TARGET_EXCLUDES_AUDIOFX := true` excludes AlphaDroid's default effects app.

Release sources, licenses, and SHA-256 checksums are recorded alongside the
prebuilts. The APK is preserved unchanged to retain its upstream signature.

Build the ROM and verify that ViPER4Android reports a working driver and
processes playback over the speaker, wired headphones, and Bluetooth with
SELinux enforcing. Runtime validation is required on hardware; investigate
any AVC denials before adding further policy permissions.
