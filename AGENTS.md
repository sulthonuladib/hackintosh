# AGENTS.md

Rules for changing this repository. The overview is in [README.md](README.md).

## Hard rules

- **Public repo.** Never commit `SystemSerialNumber`, `MLB`, `SystemUUID`, `ROM`, MACs, Apple IDs,
  FileVault keys, `.reference/`, `build/`, `devices/*/acpi/`, or local mount paths.
- **Sanitize every config before committing:** `scripts/sanitize-config.py <in> <out>`, then
  `--check <out>` (must print `ok: no identity fields set`). A sanitized snapshot is not bootable;
  the bootable copy stays on the stick and in `build/`.
- **Never send AI-written PRs, issues or reviews to the NullMoth upstreams.**

## Validate the OpenCore config with ocvalidate

Use the validator from the OpenCore release the EFI was built from. Another version only prints a
NOTE and can still say "No issues found" — that is not a result. Do not re-derive it, 1401 already
does:

```sh
scripts/ocvalidate-efi.sh devices/<machine>/efi/<target>
```

It calls `p1401/validate.py`: `_opencore_release()` reads `OCK_Files/history.json`,
`ocvalidate_path()` verifies and extracts the archive's validator, `release_components()` proves
`OpenCore.efi`/`BOOTx64.efi`/drivers match it, then `run_ocvalidate()` runs it. Current snapshots
are OpenCore **1.0.9 DEBUG**.

Expected: `Completed validating ... No issues found.` and exit 0. Record it next to the snapshot:

```sh
scripts/ocvalidate-efi.sh devices/<machine>/efi/<target> \
  | tee devices/<machine>/efi/<target>/ocvalidate-<version>.txt
```

`ocvalidate` does not check kext files/order or boot-file hashes; `p1401/validate.py` does that
during a build.

## Layout

```
devices/<machine>/README.md          identity, status, hardware, PCI/ACPI paths
devices/<machine>/hardware/          NullMoth Hardware-Sniffer reports
devices/<machine>/efi/<target>/      EFI/ + inventory.md + ocvalidate-<version>.txt
devices/<machine>/build.md           how the EFI was built
docs/                                reference.md, 1401-flow.md
scripts/                             scan-hardware.py, report-for-1401.py,
                                     sanitize-config.py, config-inventory.py, ocvalidate-efi.sh
```

## Change the EFI

1. Scan hardware: `scripts/scan-hardware.py --out devices/<machine>/hardware` (or the 1401 Probe stick).
2. Use 1401 **v2.5.2**, not `main`: `git -C .reference/1401 checkout v2.5.2`.
3. Build with `--macos 24` (Sequoia) or `--macos 25` (Tahoe); see [`docs/1401-flow.md`](docs/1401-flow.md).
4. Snapshot: copy `build/.../EFI` to `devices/<machine>/efi/<target>/EFI`, sanitize, validate,
   regenerate `inventory.md`, update `build.md`.
5. Stick: replace `EFI/` on the FAT32 partition, copy `NullMoth/system-profile.json` and the Mac
   companion. Never erase a disk without confirming the device twice.
