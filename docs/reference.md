# Reference repositories

Read-only clones of upstream projects this repo's config is based on. They live in
`.reference/` (git-ignored, never committed) and are pinned to the commits below so notes
elsewhere in this repo stay reproducible.

Re-clone / refresh:

```sh
mkdir -p .reference && cd .reference
git clone https://github.com/nullmoth/1401.git
git clone https://github.com/nullmoth/1401-probe.git
git clone https://github.com/nullmoth/nvidia-macos-driver.git
git clone https://github.com/corpnewt/gibMacOS.git
git clone https://github.com/acidanthera/OpenCorePkg.git
```

Release downloads (also git-ignored) live in `.reference/1401-probe/release/` and
`.reference/tools/opencore/<version>/`.

## Cloned

| Repo | Pinned commit | License | What it is |
|---|---|---|---|
| [nullmoth/1401](https://github.com/nullmoth/1401) | `381eec6` | PolyForm Noncommercial 1.0.0 | Windows app that reads a PC's hardware, builds an OpenCore setup and writes a macOS install USB stick ("reverse Boot Camp"). Source for the generated EFI/OpenCore config. |
| [nullmoth/1401-probe](https://github.com/nullmoth/1401-probe) | `ea28f4b` | GPL-3.0 | Offline hardware scanner on a USB stick; saves a single report (serials, UUIDs, MACs and Windows product key stripped) for sharing. Use it to inventory a build before picking SMBIOS/kexts. |
| [nullmoth/nvidia-macos-driver](https://github.com/nullmoth/nvidia-macos-driver) | `f2114ab` | PolyForm Noncommercial 1.0.0 | Metal driver for NVIDIA Turing+ cards on macOS 15 Sequoia / 26 Tahoe (Intel Macs and OpenCore PCs): `NVMTLDriver.bundle`, shader translator, NVK back end, kexts (`NVRM`, `NVAccel`, `NVRMFB`, `NVRMAGDC`). |
| [corpnewt/gibMacOS](https://github.com/corpnewt/gibMacOS) | `bf8f2ab` | MIT | Downloads macOS installers/recovery straight from Apple's software update catalogue, and builds an install app. Used to fetch the Tahoe installer instead of trusting a mirror. |
| [acidanthera/OpenCorePkg](https://github.com/acidanthera/OpenCorePkg) | `25d02c8` (1.0.8 release) | BSD-3-Clause | OpenCore itself. Source of `ocvalidate`, `Sample.plist`, `Docs/` and the reference ACPI/kext conventions. |

Not cloned on purpose: `nullmoth/nullmoth` (org profile repo, no technical content).

## Tooling pulled from releases

| What | Where | Notes |
|---|---|---|
| `ocvalidate` 1.0.8 (Linux/macOS/Windows) | `.reference/tools/opencore/1.0.8/Utilities/ocvalidate/` | Run against the sanitized config snapshots in `devices/<machine>/efi/`. Use the build that matches the OpenCore in use — version mismatches are the only thing the tool can't check. |
| `1401-probe-mac.sh`, `1401-probe-linux.py`, `1401-probe-img.zip` | `.reference/1401-probe/release/` | v2.2.0. `1401-probe-img.zip` SHA-256 `35edfb7500a86a6a7052454ce64be5a0b9b94731f1390073847c23232187eb15` (from the release's `SHA256SUMS.txt`). The Mac script scans the running Mac; the Linux script only writes the stick and fetches reports. |

## Key documents upstream

Paths are relative to `.reference/<repo>/`.

**1401** — Windows → macOS installer

- `README.md` — end-to-end usage: check PC, build setup, BIOS steps, create stick, install Mac companion.
- `docs/HOW-IT-WORKS.md` — step-by-step pipeline of the installer.
- `docs/RELEASE-1.0.24.md` — latest Windows release changes.
- `docs/PLAN.md` — project plan / scope notes.
- `upstream/` — vendored OpenCore / kext sources the installer pulls from.

**1401-probe** — offline hardware scanner

- `README.md` — what the stick does to the machine, download verification (DNS-published SHA-256).
- `build.sh` — Docker-pinned build for `all`, per-platform targets.
- `probe/`, `linux/`, `mac/`, `windows/` — scanner and host app sources.
- `CHANGELOG.md` — 2.2.0 added the Windows scan and `--scan` for a running Mac; the stick scan stays the most complete (VBIOS, CPUID/MSR, ACPI, PCI config, driver trace).
- `.reference/1401-probe/release/1401-probe-mac.sh --scan` — scan the machine you are sitting in front of, from macOS, no stick needed.

**nvidia-macos-driver** — NVIDIA Metal driver

- `README.md` — architecture: Metal app → `NVMTLDriver.bundle` → translator (AIR → SPIR-V) → NVK → kexts; on-disk install paths.
- `docs/HOW-IT-WORKS.md` — driver internals.
- `docs/CARD-SUPPORT.md` — cards reported working (Turing and newer, developed on RTX 5060).
- `docs/TROUBLESHOOTING.md` — when macOS or the driver misbehaves.
- `docs/AUTO-PRIMARY-GPU.md`, `docs/MULTI-GPU.md` — GPU selection with multiple cards.
- `docs/SLEEP-WAKE.md`, `docs/EVENT-WAIT.md` — power management and event-wait behaviour.
- `docs/NVRMFB-*` — framebuffer display/audio mapping and hotplug lifecycle.
- `kexts/`, `plugin/`, `translator/`, `nvk/` — the components themselves; `nvk/nvk-macos.patch` applies on Mesa `17ca6174`.

## General upstream references

Not cloned — external docs worth reading alongside these repos:

- [OpenCore Install Guide](https://dortania.github.io/OpenCore-Install-Guide/) — manual OpenCore setup when 1401 doesn't cover the board.
- [OpenCorePkg releases](https://github.com/acidanthera/OpenCorePkg/releases) — bootloader releases and `Sample.plist`.
- [Dortania builds](https://dortania.github.io/builds/) — kext/OpenCore build index.
- [OpenCore config docs](.reference/OpenCorePkg/Docs/Configuration.pdf) — canonical meaning of every `config.plist` key.
