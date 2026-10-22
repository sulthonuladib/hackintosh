#!/usr/bin/env python3
"""Run NullMoth's Hardware-Sniffer Linux collector — the one 1401 itself uses — on this machine.

The 1401 Probe USB stick is the complete scanner (VBIOS, CPUID/MSRs, ACPI tables, PCI config
space, driver traces), but it needs a spare stick and a reboot. This runs the same collector that
the stick runs, straight from the running Linux, and writes the `Report.json` in the format the
1401 EFI builder reads.

It only reads: /sys, /proc, lspci and lsusb. No root, nothing uploaded.

    scripts/scan-hardware.py --out devices/<machine>/hardware
    scripts/scan-hardware.py --probe-repo /path/to/1401-probe --out ...

Needs the 1401-probe source checked out under `.reference/1401-probe` (see docs/reference.md).
"""
import argparse
import contextlib
import datetime
import json
import os
import sys

REPO_HINT = "git clone https://github.com/nullmoth/1401-probe.git .reference/1401-probe"


class Tee:
    def __init__(self, stream):
        self.stream = stream
        self.parts = []

    def write(self, text):
        self.stream.write(text)
        self.stream.flush()
        self.parts.append(text)

    def flush(self):
        self.stream.flush()

    def text(self):
        return "".join(self.parts)


def find_hsniffer(probe_repo=None):
    roots = []
    if probe_repo:
        roots.append(probe_repo)
    if os.environ.get("PROBE_REPO"):
        roots.append(os.environ["PROBE_REPO"])
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    roots.append(os.path.join(here, ".reference", "1401-probe"))
    for root in roots:
        path = os.path.join(root, "probe", "overlay", "usr", "lib", "1401-probe", "hsniffer")
        if os.path.isdir(os.path.join(path, "Scripts")):
            return path
    sys.exit(
        "1401-probe source not found. Clone it first:\n\n  %s\n" % REPO_HINT
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--probe-repo", help="path to the 1401-probe checkout (default: .reference/1401-probe)")
    ap.add_argument("--out", help="directory for <date>-hsniffer-Report.json and the collector log")
    ap.add_argument("--label", default=datetime.date.today().isoformat(), help="file name prefix (default: today)")
    args = ap.parse_args()

    hsniffer = find_hsniffer(args.probe_repo)
    sys.path.insert(0, hsniffer)
    from Scripts.platforms.linux import LinuxHardwareInfo  # noqa: PLC0415

    print("collector: %s" % hsniffer)
    tee = Tee(sys.stdout)
    hw = LinuxHardwareInfo(rich_format=False)
    with contextlib.redirect_stdout(tee):
        hw.hardware_collector()

    if not hw.result:
        sys.exit("collector returned no sections")

    report = json.dumps(hw.result, indent=2) + "\n"
    if not args.out:
        sys.stdout.write(report)
        return

    os.makedirs(args.out, exist_ok=True)
    json_path = os.path.join(args.out, "%s-hsniffer-Report.json" % args.label)
    log_path = os.path.join(args.out, "%s-hsniffer-collector.log" % args.label)
    with open(json_path, "w") as f:
        f.write(report)
    with open(log_path, "w") as f:
        f.write(tee.text())

    print("\nsections: %s" % ", ".join(sorted(hw.result)))
    print("wrote %s" % json_path)
    print("wrote %s" % log_path)


if __name__ == "__main__":
    main()
