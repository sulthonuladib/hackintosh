# Hackintosh

macOS-on-PC configuration for my machines: hardware scans, OpenCore EFI snapshots, and the build
that went on each installer stick.

## Current machine

[**msi-pro-b650m-p**](devices/msi-pro-b650m-p/) — MSI PRO B650M-P, Ryzen 7 7800X3D, RTX 4070 Ti SUPER.

- **Sequoia 15** — EFI built, validated, on the Sequoia stick.
- **Tahoe 26** — EFI built and validated, waiting for a Tahoe recovery medium.

## Repository

| Path | What |
|---|---|
| [`devices/`](devices/) | one directory per machine: hardware scan, `efi/` snapshots, `build.md` |
| [`docs/`](docs/) | [upstream repos and tools](docs/reference.md), [the 1401 flow](docs/1401-flow.md) |
| [`scripts/`](scripts/) | hardware scan, report fixup, config sanitize/inventory, matched `ocvalidate` |
| [`AGENTS.md`](AGENTS.md) | rules for changing this repository |

`.reference/` (upstream clones and tools) and `build/` (EFI output with generated SMBIOS identity)
are git-ignored. This repository is public; [`AGENTS.md`](AGENTS.md) lists what is never committed.
