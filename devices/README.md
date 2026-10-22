# Devices

One directory per machine, holding what it actually is (hardware dump) and what we boot on
it (OpenCore config state), so a config change can be traced back to a scan.

## Layout

```
devices/<vendor>-<model>-<short>/
  README.md        identity, status, hardware we know and how we know it
  hardware/        hardware dumps: 1401-probe reports, derived notes, scan runbook
  efi/             sanitized OpenCore config snapshots + ocvalidate results
  notes/           optional: install attempts, boot failures, fixes
```

## Rules

- **This repository is public.** Never commit `SystemSerialNumber`, `MLB`, `SystemUUID`, `ROM`,
  Wi-Fi/Bluetooth MAC addresses, Apple ID, FileVault keys, or a raw EFI directory.
  `scripts/sanitize-config.py` strips the identity fields from a `config.plist` before it is added.- 1401-probe reports are redacted by the tool itself (serials, UUIDs, MAC/BT addresses, Wi-Fi
  names, paired-device names, computer and user names). Read them once before committing anyway.
- Every hardware claim in a machine's `README.md` states where it came from: a probe report, an
  OpenCore log, or "unverified".
- Local mount paths of removable media are not recorded in this repo. Refer to "the installer
  stick" or "the probe stick" instead.
- Don't commit EFI binaries, kexts, or `OpenCore.efi`. Track `config.plist`, its ACPI/kext/driver
  inventory, and `ocvalidate` output.

## Machines

| Directory | Machine | CPU / GPU | Target | Scan |
|---|---|---|---|---|
| [`msi-pro-b650m-p`](msi-pro-b650m-p/) | MSI PRO B650M-P (MS-7E27) | Ryzen 7 7800X3D / RTX 4070 Ti SUPER + Radeon 610M | macOS 26 Tahoe (NullMoth NVIDIA driver) | done — Hardware-Sniffer |

## Scanning

`scripts/scan-hardware.py` runs NullMoth's Hardware-Sniffer Linux collector from the running OS
and writes the `Report.json` that 1401's EFI builder reads. The 1401 Probe USB stick remains the
complete scanner (VBIOS, ACPI, CPUID/MSRs, PCI config, driver traces) when a spare stick is
available. Details per machine, in `hardware/README.md`.
