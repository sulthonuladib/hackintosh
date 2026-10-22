# Hackintosh

this is where i track all config of my hackintosh devices

## Documents

- [Devices](devices/) — per-machine hardware dumps and OpenCore config state. Current machine:
  [msi-pro-b650m-p](devices/msi-pro-b650m-p/).
- [Reference repositories](docs/reference.md) — upstream projects this config is based on (cloned into git-ignored `.reference/`, pinned commits and key docs).
- [Scripts](scripts/) — `scan-hardware.py` (NullMoth Hardware-Sniffer from the running OS),
  `sanitize-config.py` (strip SMBIOS identity before committing a config) and
  `config-inventory.py` (Markdown inventory of a `config.plist`).
