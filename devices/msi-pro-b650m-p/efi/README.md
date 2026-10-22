# EFI snapshots — msi-pro-b650m-p

The EFIs 1401 built for this machine, committed so configuration changes are reviewable in git.
Each directory is a complete `EFI/` tree (OpenCore 1.0.9, `BOOTx64.efi`, drivers, kexts, ACPI
SSDTs), not just the plist.

| Directory | Target | Built with | Config |
|---|---|---|---|
| [`sequoia/`](sequoia/) | macOS 15 Sequoia (`24.99.99`), SMBIOS `MacPro7,1` | 1401 v2.5.2 | AppleALC, RTL812xLucy, NVIDIA policy |
| [`tahoe/`](tahoe/) | macOS 26 Tahoe (`25.99.99`), SMBIOS `MacPro7,1` | 1401 v2.5.2 | VoodooHDA (manual), `revpatch=sbvmm`, NVIDIA policy |

Each has `inventory.md` (generated from the config by `scripts/config-inventory.py`) and the
`ocvalidate` output for 1.0.9 (the OpenCore release in the EFI) and 1.0.8 (the newest release
validator kept in `.reference/tools`). Both report **no issues**. Validation is mandatory before
any commit: see [`AGENTS.md`](../../../AGENTS.md#validate-the-opencore-config-with-ocvalidate).

## The config here is sanitized

`config.plist` in these snapshots has `SystemSerialNumber`, `MLB`, `SystemUUID` blanked and `ROM`
zeroed by `scripts/sanitize-config.py`. This repository is public and those fields are the
machine's Apple identity.

That means **a snapshot is not bootable as-is**. The bootable copies are:

- on the Sequoia stick (`EFI/OC/config.plist`, real identity),
- in the git-ignored build output (`build/msi-pro-b650m-p/out-sequoia/`, `build/msi-pro-b650m-p/out/`).

Generate a new identity by rebuilding with 1401 (it runs `macserial`), or fill the four fields
with `macserial -g --model MacPro7,1` output (`MLB`/serial) plus a random 6-byte `ROM` and a UUID.

## Refresh a snapshot

```sh
# 1. copy the new build
rm -rf devices/msi-pro-b650m-p/efi/sequoia
cp -a build/msi-pro-b650m-p/out-sequoia/EFI devices/msi-pro-b650m-p/efi/sequoia

# 2. strip identity and prove it
scripts/sanitize-config.py devices/msi-pro-b650m-p/efi/sequoia/OC/config.plist \
  devices/msi-pro-b650m-p/efi/sequoia/OC/config.plist
scripts/sanitize-config.py --check devices/msi-pro-b650m-p/efi/sequoia/OC/config.plist

# 3. validate with the matching OpenCore release and record it
.reference/tools/opencore/1.0.9/Utilities/ocvalidate/ocvalidate.linux \
  devices/msi-pro-b650m-p/efi/sequoia/OC/config.plist \
  | tee devices/msi-pro-b650m-p/efi/sequoia/ocvalidate-1.0.9.txt

# 4. inventory
scripts/config-inventory.py devices/msi-pro-b650m-p/efi/sequoia/OC/config.plist \
  > devices/msi-pro-b650m-p/efi/sequoia/inventory.md
```

Then update [`../build.md`](../build.md), the table above, and commit. Keep `build/` and the ACPI
dump out of git (both ignored): they carry identity and firmware data.

## History

- 2026-10-22 — first snapshots: Sequoia and Tahoe, both `ocvalidate` clean. Sequoia is the one on
  the stick (the sticks carry Sequoia recovery); Tahoe waits for a Tahoe recovery medium.
