# msi-pro-b650m-p

The desktop this repository lives on. Target: macOS 26 Tahoe with the RTX 4070 Ti SUPER driven by
the NullMoth NVIDIA driver.

|          |                                                                                                                       |
| -------- | --------------------------------------------------------------------------------------------------------------------- |
| Board    | MSI PRO B650M-P (MS-7E27), AM5, B650                                                                                  |
| BIOS     | `1.G0`, 2025-06-20, UEFI — Secure Boot disabled, Above 4G Decoding enabled, Resizable BAR enabled                     |
| CPU      | AMD Ryzen 7 7800X3D — Raphael, 8 cores / 16 threads, AVX2 (no AVX-512)                                                |
| dGPU     | NVIDIA GeForce RTX 4070 Ti SUPER — AD102, `10de:2689`, 16 GB, `01:00.0`, ReBAR on                                     |
| iGPU     | AMD Radeon 610M (Raphael) — `1002:164e`, no macOS driver                                                              |
| RAM      | 30 GiB                                                                                                                |
| Network  | Realtek RTL8125 2.5GbE — `10ec:8125`. No Wi-Fi, no Bluetooth                                                          |
| Audio    | Realtek ALC897 — `10ec:0897` (`1462:9e27`); NVIDIA HDMI audio `10de:00a3`; AMD HDMI audio `1002:1640`                 |
| Storage  | ADATA LEGEND 850 LITE 465.8 GB NVMe (`1cc1:628a`); TEAM TM8FP6001T 953.9 GB NVMe (`126f:2263`); ST1000DM003 1 TB SATA |
| USB      | 4 controllers: `1022:15b6`, `1022:15b7`, `1022:15b8` (CPU) and `1022:43f7` (B650 chipset)                             |
| Displays | 2 × 2560×1440 over DisplayPort, both on the RTX                                                                       |
| Other    | TPM 2.0, MSI Mystic Light USB, Audient iD4 USB audio, ANYKA FHD camera                                                |

## Status

| Step                                                                             | State                                        |
| -------------------------------------------------------------------------------- | -------------------------------------------- |
| Hardware scan (NullMoth Hardware-Sniffer, run from this OS)                      | done — [`hardware/`](hardware/)              |
| Full 1401 Probe stick report (VBIOS, ACPI, CPUID/MSR, PCI config, driver traces) | optional, needs a spare stick                |
| Sequoia EFI (1401 v2.5.2 on Linux)                                               | built + `ocvalidate` clean, on the Sequoia stick — [`build.md`](build.md) |
| Tahoe EFI                                                                        | built + `ocvalidate` clean, waiting for a Tahoe recovery — [`build.md`](build.md) |
| macOS install                                                                    | next: boot the stick                         |

## PCI paths (for `DeviceProperties` / ACPI)

| Device                | PCI path                                                           | ACPI path                       |
| --------------------- | ------------------------------------------------------------------ | ------------------------------- |
| RTX 4070 Ti SUPER     | `PciRoot(0x0)/Pci(0x1,0x1)/Pci(0x0,0x0)`                           | `\_SB.PCI0.GPP0.VGA_`           |
| RTX HDMI audio        | `PciRoot(0x0)/Pci(0x1,0x1)/Pci(0x0,0x1)`                           | `\_SB.PCI0.GPP0.HDAU`           |
| Radeon 610M           | `PciRoot(0x0)/Pci(0x8,0x1)/Pci(0x0,0x0)`                           | `\_SB.PCI0.GP17.VGA_`           |
| ALC897 HDA controller | `PciRoot(0x0)/Pci(0x8,0x1)/Pci(0x0,0x6)`                           | `\_SB.PCI0.GP17.AZAL`           |
| ADATA NVMe            | `PciRoot(0x0)/Pci(0x1,0x2)/Pci(0x0,0x0)`                           | `\_SB.PCI0.GPP1.NVME`           |
| TEAM NVMe             | `PciRoot(0x0)/Pci(0x2,0x1)/Pci(0x0,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)` | `\_SB.PCI0.GPP7.UP00.DP00.NV00` |
| RTL8125               | `PciRoot(0x0)/Pci(0x2,0x1)/Pci(0x0,0x0)/Pci(0xa,0x0)/Pci(0x0,0x0)` | —                               |

## What this means for macOS

- **Graphics**: the RTX 4070 Ti SUPER is Ada, inside the NullMoth driver's Turing-and-later range,
  but that family's physical validation is still listed as pending — treat the desktop as
  unproven until it boots. The driver's tested setup is Resizable BAR **on**; 1401 installs with a
  small BAR (`ResizeAppleGpuBars 0`, `ResizeGpuBars -1`) and the Mac app restores the full BAR
  after install.
- **iGPU**: the Radeon 610M has no macOS driver. The desktop must present through the NVIDIA card;
  keep the iGPU out of the config.
- **CPU**: 1401 has an AMD path (memory-map quirks for `DevirtualiseMmio`/`SetupVirtualMap`, IOMMU
  off, no CFG Lock) and ships `AMDRyzenCPUPowerManagement`/`SMCRadeonGPU`.
- **Audio**: ALC897 needs `AppleALC`; Tahoe dropped `AppleHDA`, so this is the OCLP-rollback path
  that also means SIP/AMFI changes.
- **Ethernet**: RTL8125, not the RTL8111 the old EFI carried.
- **Wireless**: nothing to configure — and no AirDrop/Handoff/Continuity without a supported card.
- **Storage**: both NVMe drives are on supported controllers; no Intel VMD (AMD platform).

## Gaps in this scan

The Hardware-Sniffer collector reads what the running OS exposes. It does not read the GPU VBIOS,
ACPI tables, CPUID/MSRs, PCI configuration space or memory-module SPD — the 1401 Probe USB stick
does. Nothing here identifies the machine personally (no serials, no UUIDs, no MACs).

## Layout

- [`hardware/2026-10-22-hsniffer-Report.json`](hardware/2026-10-22-hsniffer-Report.json) — raw
  report, the format 1401's builder reads.
- [`hardware/2026-10-22-hsniffer-collector.log`](hardware/2026-10-22-hsniffer-collector.log) —
  collector progress log.
- [`hardware/README.md`](hardware/README.md) — how the scan was made and how to repeat it.
- [`efi/`](efi/) — committed Sequoia and Tahoe EFI snapshots. The `config.plist` there is
  sanitized (not bootable as-is); each snapshot has its `ocvalidate` output and `inventory.md`.
- [`build.md`](build.md) — how both EFIs were built with 1401 v2.5.2 on Linux, and the caveats.
