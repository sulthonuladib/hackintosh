# Hackintosh

this is where i track all config of my hackintosh devices

## Documents

- [Devices](devices/) — per-machine hardware dumps and OpenCore config state. Current machine:
  [msi-pro-b650m-p](devices/msi-pro-b650m-p/).
- [AGENTS.md](AGENTS.md) — rules for changing this repo, including the mandatory `ocvalidate` step.
- [Reference repositories](docs/reference.md) — upstream projects this config is based on (cloned into git-ignored `.reference/`, pinned commits and key docs).
- [1401 flow](docs/1401-flow.md) — how the Windows 1401 app works step by step (C# shell → Python engine → OpenCore build → stick) and how to run the same engine on Linux without Windows.
- [Scripts](scripts/) — `scan-hardware.py` (NullMoth Hardware-Sniffer from the running OS),
  `sanitize-config.py` (strip SMBIOS identity before committing a config),
  `config-inventory.py` (Markdown inventory of a `config.plist`) and
  `report-for-1401.py` (drop the ACPI paths 1401's validator rejects).
