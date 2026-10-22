# EFI builds — msi-pro-b650m-p

Two builds from the same scan and ACPI dump, both produced on Linux by the 1401 engine at tag
**v2.5.2** (`fc09d19`). The Windows app was not involved: it is a C# shell around these modules —
see [`docs/1401-flow.md`](../../../docs/1401-flow.md).

| Target | Result | SMBIOS | Audio | Where |
|---|---|---|---|---|
| macOS 15 Sequoia (Darwin `24.99.99`) | ok, `ocvalidate` 1.0.9 clean | `MacPro7,1` | `AppleALC` | [`efi/sequoia/`](efi/sequoia/) + the Sequoia stick |
| macOS 26 Tahoe (Darwin `25.99.99`) | ok, `ocvalidate` 1.0.9 clean | `MacPro7,1` | VoodooHDA, installed after macOS | [`efi/tahoe/`](efi/tahoe/) (waiting for a Tahoe recovery) |

`build/` is ignored because a built `config.plist` carries generated `SystemSerialNumber`, `MLB`
and `SystemUUID`. The committed snapshots in [`efi/`](efi/) have those four fields blanked by
`scripts/sanitize-config.py`; they are for review, not for booting.

## Inputs

```sh
# 1401 v2.5.2 — the released version, not main (main is older and caps NVIDIA at Sequoia)
git -C .reference/1401 checkout v2.5.2

# The report 1401's own pinned Hardware-Sniffer makes on Linux.
# (Produced without its ACPI step; the ACPI tables come from the root copy.)
build/msi-pro-b650m-p/scan/Report.json

# 1401's report validator only accepts _SB paths. The Linux collector emits two root-level
# devices (\HPET and \AOD_), so those two ACPI Path values are removed. Nothing else changes.
scripts/report-for-1401.py build/msi-pro-b650m-p/scan/Report.json \
  build/msi-pro-b650m-p/scan/Report.1401.json

# /sys/firmware/acpi/tables, copied as root, one file per table, named <sig>.aml.
# Git-ignored: firmware tables can carry board serials/IDs.
devices/msi-pro-b650m-p/acpi/
```

## Commands

```sh
cd .reference/1401

# Sequoia
python3 -m p1401 build ../../build/msi-pro-b650m-p/scan/Report.1401.json \
  ../../devices/msi-pro-b650m-p/acpi ../../build/msi-pro-b650m-p/out-sequoia \
  --macos 24 --json

# Tahoe
python3 -m p1401 build ../../build/msi-pro-b650m-p/scan/Report.1401.json \
  ../../devices/msi-pro-b650m-p/acpi ../../build/msi-pro-b650m-p/out \
  --macos 25 --json
```

`plan` is the same call without an output directory and without downloads; it is useful before a
build.

## What the engine decided

Both builds:

- Disabled: `Integrated GPU: Radeon 610M` (`1002-164E`) and `Sound: Nvidia GPU a3 HDMI/DP`
  (`10DE-00A3`).
- SMBIOS `MacPro7,1` — the model that runs both macOS 15 and 26 with a desktop GPU (macOS 26
  refuses `iMacPro1,1`).
- NVIDIA policy: boot-args `nvfb=1 nvaccel=1 nvfbheads=4 -nvkmsnosmooth amfi_get_out_of_my_way=0x1
  amfi=0x80 ipc_control_port_options=0`, `csr-active-config 0x0A43`, `gfxrst=4`,
  `ResizeAppleGpuBars 0` / `ResizeGpuBars -1` (installer screen with a large BAR).
- AMD policy: `DisableVariableWrite = True`, `AllowRelocationBlock = True`.
- Boot logs onto the stick (`Target 67`, `AppleDebug`, `ApplePanic`), boot-args never deleted from
  NVRAM, installer entry visible.

Sequoia additionally enables `AppleALC` (ALC897, layout default 98). Tahoe has no `AppleHDA`
anymore, so the engine chose VoodooHDA; that kext is **not** in the EFI and must be injected into
`/Library/Extensions` after installation. Tahoe also adds `revpatch=sbvmm`.

Kexts in the Sequoia EFI: `Lilu`, `AMFIPass`, `AppleALC`, `AppleMCEReporterDisabler`, `NVMeFix`,
`RTL812xLucy`, `RestrictEvents`, `USBToolBox`, `UTBDefault`, `VirtualSMC`, `WhateverGreen`.

ACPI in both: `SSDT-EC`, `SSDT-PLUG-ALT`, `SSDT-USB-Reset`, `SSDT-USBX`.

## The Sequoia stick

The existing stick is a Sequoia installer, so its recovery matches the Sequoia build. It was
updated in place:

```
EFI/                                  replaced with the built Sequoia EFI
com.apple.recovery.boot/              left as-is (Sequoia)
NullMoth/system-profile.json          the build's machine profile
NullMoth/1401-Mac-2.4.3.dmg           the Mac companion that installs the NVIDIA driver
```

`ocvalidate` against the copied `EFI/OC/config.plist`: no issues.

## Caveats

- **Ada is unvalidated.** The RTX 4070 Ti SUPER is in the driver's device table, but the driver
  repo lists RTX 40 physical validation as pending. A clean `ocvalidate` says nothing about a
  working desktop.
- **First boot is the open risk**, not the config: AMD memory map/IOMMU, the installer's screen
  with a large BAR, and the absence of a driver during installation. Boot with `-v`; the stick is
  configured to leave OpenCore and Apple boot logs on the FAT32 partition.
- **Tahoe needs its own recovery.** The sticks carry Sequoia recovery; installing Tahoe means
  fetching Apple's Tahoe recovery image onto a stick (about 850 MB) or using a Tahoe installer
  medium. The Tahoe EFI can wait in `build/` until then.
- **No Wi-Fi/Bluetooth** on this board; only the RTL8125 Ethernet kext is included.
- The 1401 clone must stay at `v2.5.2`: `main` is older and its `SEQUOIA` cap rejects Tahoe.
