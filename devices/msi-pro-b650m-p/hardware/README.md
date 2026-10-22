# Hardware scan — msi-pro-b650m-p

Taken with NullMoth's **Hardware-Sniffer** Linux collector, the same collector bundled in
[1401 Probe v2.2.0](https://github.com/nullmoth/1401-probe) that produces the `Report.json` the
1401 EFI builder reads. It is not the bootable stick: it runs from inside this OS, needs no root
and no reboot, and only reads `/sys`, `/proc`, `lspci` and `lsusb`.

## Files

| File | What |
|---|---|
| `2026-10-22-hsniffer-Report.json` | raw report, unmodified; sections `BIOS`, `CPU`, `GPU`, `Input`, `Monitor`, `Motherboard`, `Network`, `Sound`, `Storage Controllers`, `System Devices`, `USB Controllers` |
| `2026-10-22-hsniffer-collector.log` | the collector's progress log for that run |

## Repeat it

```sh
# one-time: the collector comes from the 1401-probe source (git-ignored)
git clone https://github.com/nullmoth/1401-probe.git .reference/1401-probe

scripts/scan-hardware.py --out devices/msi-pro-b650m-p/hardware --label "$(date +%F)"
```

The script only uses the collector; it prints progress, writes the JSON and log, and prints the
section list. It fails with the clone command if `.reference/1401-probe` is missing. Pass
`--probe-repo /path/to/1401-probe` to use a checkout elsewhere.

The stick path (`1401-probe-mac.sh --scan`, the Windows app scan, or `1401-probe-linux.py` +
booting the probe image) is still the complete scanner: it adds the GPU VBIOS, CPUID/MSRs, ACPI
tables, PCI configuration space, the USB port topology and a driver trace. Use it when a spare
USB stick is available; it is the report NullMoth asks for when a board misbehaves.

## What this scan does not have

- GPU VBIOS / expansion ROM contents and PCI config space — the stick reads those.
- ACPI tables and the firmware memory map — the stick dumps them; useful for `DevirtualiseMmio`
  white-listing and `SSDT-PLUG`/`SSDT-EC` work.
- CPUID leaves and MSRs — the stick records them; the collector only reports the vendor, codename
  and SIMD flags.
- Memory modules and SPD — the container reads `/sys`, which does not expose SPD; the report has
  only the total (`free -h`: 30 GiB), not per-DIMM part numbers.
- The collector says `Core Count: 16` for this CPU. That is the logical processor count; the
  Ryzen 7 7800X3D has 8 cores / 16 threads.

## Privacy

Nothing that identifies the machine personally is in these files: no serial numbers, no UUIDs, no
MAC addresses, no Windows product key. The collector does not call `dmidecode`, so it cannot read
the board/chassis serials at all. This repository is public; keep it that way when re-running the
scan.
