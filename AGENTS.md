# AGENTS.md

Rules for anyone — human or AI — changing this repository.

## What this is

One directory per hackintosh machine under `devices/`: what the hardware is, the OpenCore config
progression, and the exact EFI that went on an installer stick. The machine tracked today is
[`devices/msi-pro-b650m-p/`](devices/msi-pro-b650m-p/) (MSI PRO B650M-P, Ryzen 7 7800X3D,
RTX 4070 Ti SUPER).

```
devices/<machine>/
  README.md          identity, status, known hardware, PCI/ACPI paths
  hardware/          hardware scans (NullMoth Hardware-Sniffer reports) + runbook
  efi/               committed EFI snapshots, one directory per macOS target
  build.md           how the EFI was built (1401 version, commands, decisions, caveats)
docs/
  reference.md       upstream repos and tools, pinned commits
  1401-flow.md       how the Windows 1401 app works and how to run the engine on Linux
scripts/
  scan-hardware.py   run NullMoth's Hardware-Sniffer from this OS
  report-for-1401.py make a report pass 1401's validator
  sanitize-config.py blank SMBIOS identity before committing a config
  config-inventory.py Markdown inventory of a config.plist
.reference/          git-ignored upstream clones + downloaded tools (1401 v2.5.2, OpenCorePkg, ocvalidate, 1401 Probe)
build/               git-ignored 1401 output (EFI with generated SMBIOS identity)
```

## Public repository: identity never goes in

The repository is public. Never commit:

- `SystemSerialNumber`, `MLB`, `SystemUUID`, `ROM` from `PlatformInfo/Generic`
- Wi-Fi/Bluetooth MAC addresses, Apple IDs, FileVault keys
- raw EFI directories from a stick, `build/`, `.reference/`
- `devices/*/acpi/` (firmware tables can carry board serials/IDs)
- local mount paths such as `/run/media/...`

Before committing a `config.plist`:

```sh
scripts/sanitize-config.py <in.plist> <out.plist>
scripts/sanitize-config.py --check <out.plist>      # must print: ok: no identity fields set
```

A sanitized snapshot is **not bootable as-is**. The bootable copy stays on the stick and in
git-ignored `build/`; the snapshot exists so config changes are diffable.

## Validate the OpenCore config with ocvalidate

OpenCore ships its own validator. A plist that parses — or that 1401 built — is not proof the
snapshot is still valid: `sanitize-config.py` rewrites it and people edit it. **Run `ocvalidate` on
every config before committing.**

Use the validator that matches the OpenCore version in the EFI. Both current snapshots are
OpenCore **1.0.9** (the build log says `OC: OpenCore DBG-109-... is loading`).

```sh
.reference/tools/opencore/1.0.9/Utilities/ocvalidate/ocvalidate.linux \
  devices/msi-pro-b650m-p/efi/sequoia/OC/config.plist
```

Expected output and exit status 0:

```
Completed validating .../config.plist in 1 ms. No issues found.
```

`Found N issues`, a version mismatch, or a non-zero exit means fix the config — do not commit it.
If `.reference/` is missing, the validator comes from the matching
[OpenCorePkg release](https://github.com/acidanthera/OpenCorePkg/releases)
(`Utilities/ocvalidate/ocvalidate.linux`); see `docs/reference.md`.

Record the result next to the snapshot and update it whenever the config changes:

```sh
.reference/tools/opencore/1.0.9/Utilities/ocvalidate/ocvalidate.linux \
  devices/msi-pro-b650m-p/efi/sequoia/OC/config.plist \
  | tee devices/msi-pro-b650m-p/efi/sequoia/ocvalidate-1.0.9.txt
```

Also validate after copying a config to a stick (that copy has identity; validate it in place,
never commit it):

```sh
.reference/tools/opencore/1.0.9/Utilities/ocvalidate/ocvalidate.linux \
  /path/to/stick/EFI/OC/config.plist
```

What `ocvalidate` does **not** check: kext load order, files actually present on disk, missing
drivers or SSDTs, and the boot files matching the OpenCore release. `p1401/validate.py` does those
during a build. A clean `ocvalidate` is the minimum, not proof that the machine boots.

## Changing the EFI

1. **Scan** (if hardware changed): `scripts/scan-hardware.py --out devices/<machine>/hardware`.
   The full 1401 Probe stick is the complete scanner; see the machine's `hardware/README.md`.
2. **Prepare 1401**: the engine is the release tag, not `main`:
   `git -C .reference/1401 checkout v2.5.2`. `--macos 24` is Sequoia, `--macos 25` is Tahoe.
3. **Build**: commands are in [`docs/1401-flow.md`](docs/1401-flow.md) and the machine's
   `build.md`. Output goes to `build/` (ignored).
4. **Snapshot**: copy the built `EFI/` into `devices/<machine>/efi/<target>/`, sanitize the config,
   run `ocvalidate` (above), regenerate `inventory.md` with `scripts/config-inventory.py`, and
   update `build.md` + the snapshot table.
5. **Stick**: not with `p1401.usbwriter` on Linux. Replace `EFI/` on the FAT32 partition, copy
   `NullMoth/system-profile.json` and the Mac companion, then validate the config on the stick.

Never erase a disk without confirming the device twice (`lsblk`): a wrong device is unrecoverable.

## Upstream

`.reference/` holds third-party code under its own licenses. The NullMoth repositories ask that
contributions be written by the person submitting them — do not send AI-written pull requests,
issues or review comments upstream (see `.reference/1401/AGENTS.md`). Use the code locally to
understand and test.
