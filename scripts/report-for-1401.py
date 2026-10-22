#!/usr/bin/env python3
"""Make a Hardware-Sniffer report acceptable to 1401's report validator.

1401's validator (upstream/OpCore-Simplify/Scripts/report_validator.py) only accepts ACPI paths
under `_SB`: `^[\\]?_SB(\\.[A-Z0-9_]+)+$`. The Linux collector also emits root-level devices with
paths like `\\HPET` and `\\AOD_`, which are not used for any build decision (they are HPET and an
AOD device). This removes just those `ACPI Path` values, leaving the device entries in place.

It does not change any other key. The raw report stays untouched; write the result next to it or
into the git-ignored build directory.

    scripts/report-for-1401.py <Report.json> <out.json>
"""
import json
import re
import sys

ACPI_PATH = re.compile(r"^[\\]?_SB(\.[A-Z0-9_]+)+$")


def scrub(node, path, removed):
    if isinstance(node, dict):
        for key in list(node):
            value = node[key]
            here = "%s.%s" % (path, key) if path else key
            if key == "ACPI Path" and isinstance(value, str) and not ACPI_PATH.match(value):
                removed.append((here, value))
                del node[key]
            else:
                scrub(value, here, removed)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            scrub(item, "%s[%d]" % (path, i), removed)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, "rb") as f:
        report = json.load(f)
    removed = []
    scrub(report, "", removed)
    with open(dst, "w") as f:
        json.dump(report, f, indent=2)
        f.write("\n")
    for where, value in removed:
        print("removed %s = %r" % (where, value))
    print("wrote %s (%d ACPI Path values removed)" % (dst, len(removed)))


if __name__ == "__main__":
    main()
