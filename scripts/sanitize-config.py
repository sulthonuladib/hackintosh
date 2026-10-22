#!/usr/bin/env python3
"""Copy an OpenCore config.plist with Apple identity fields removed.

The repository is public, so the SMBIOS identity (serial, MLB, UUID, ROM) must never be
committed. Everything else is kept so config changes stay reviewable.

    scripts/sanitize-config.py <config.plist> <out.plist>
    scripts/sanitize-config.py --check <out.plist>

--check exits non-zero if any identity field still carries a value.
"""
import argparse
import plistlib
import sys

# Keys that identify one Mac (or one Apple account) and must not be published.
IDENTITY_KEYS = {
    "systemserialnumber",
    "mlb",
    "systemuuid",
    "rom",
    "serialnumber",
    "boardserialnumber",
    "hw.serialnumber",
}
ZERO_ROM = b"\x00" * 6


def walk(node, hits):
    if isinstance(node, dict):
        for key, value in list(node.items()):
            if key.lower() in IDENTITY_KEYS:
                hits.append(key)
                node[key] = ZERO_ROM if isinstance(value, bytes) else ""
            else:
                walk(value, hits)
    elif isinstance(node, list):
        for item in node:
            walk(item, hits)
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="fail if identity fields are not empty")
    ap.add_argument("config")
    ap.add_argument("out", nargs="?")
    args = ap.parse_args()

    with open(args.config, "rb") as f:
        cfg = plistlib.load(f)

    if args.check:
        dirty = []
        for path, value in iter_identity(cfg):
            if value not in ("", ZERO_ROM, None):
                dirty.append(path)
        if dirty:
            print("identity fields still set: " + ", ".join(dirty), file=sys.stderr)
            return 1
        print("ok: no identity fields set")
        return 0

    if not args.out:
        ap.error("out.plist is required unless --check is used")

    removed = walk(cfg, [])
    with open(args.out, "wb") as f:
        plistlib.dump(cfg, f, sort_keys=True)
    print("wrote %s (redacted: %s)" % (args.out, ", ".join(sorted(set(removed))) or "none"))


def iter_identity(node, prefix=""):
    if isinstance(node, dict):
        for key, value in node.items():
            path = prefix + "/" + key
            if key.lower() in IDENTITY_KEYS:
                yield path, value
            else:
                yield from iter_identity(value, path)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            yield from iter_identity(item, "%s[%d]" % (prefix, i))


if __name__ == "__main__":
    sys.exit(main())
