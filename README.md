# Common device tree for Xiaomi MT6768 devices

## ViPER4Android

This tree bundles [ViPER4Android 2.1.0](https://github.com/likelikeslike/ViPER4Android/releases/tag/2.1.0)
and the ARM/ARM64 drivers from [ViPER4Android RE 2.1.0](https://github.com/likelikeslike/ViPERFX_RE/releases/tag/v2.1.0)
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
