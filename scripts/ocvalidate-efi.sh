#!/usr/bin/env bash
# Validate an EFI's config.plist with the ocvalidate from the exact OpenCore release it was built
# from. A newer/older validator may accept a config it cannot judge (it only prints a NOTE), so
# first prove the EFI's boot files are byte-identical to the release archive, then run that
# archive's validator.
#
#   scripts/ocvalidate-efi.sh <efi-dir> [config.plist]
#   OPENCORE_ZIP=/path/OpenCore-1.0.9-DEBUG.zip scripts/ocvalidate-efi.sh <efi-dir>
#
# The archive is found from 1401's download history (OCK_Files/history.json) and ~/.cache/1401.
set -euo pipefail

efi=${1:?usage: scripts/ocvalidate-efi.sh <efi-dir> [config.plist]}
cfg=${2:-$efi/OC/config.plist}
root=$(cd "$(dirname "$0")/.." && pwd)

[ -f "$cfg" ] || { echo "no config at $cfg" >&2; exit 2; }
[ -f "$efi/OC/OpenCore.efi" ] || { echo "$efi is not an EFI directory" >&2; exit 2; }

zip=${OPENCORE_ZIP:-}
if [ -z "$zip" ]; then
    hist="$root/.reference/1401/upstream/OpCore-Simplify/OCK_Files/history.json"
    if [ -f "$hist" ]; then
        name=$(python3 - "$hist" <<'PY'
import json, sys
for item in json.load(open(sys.argv[1])):
    if item.get("product_name") == "OpenCorePkg":
        print(item["url"].rsplit("/", 1)[-1])
        break
PY
        )
        [ -n "$name" ] && zip="$HOME/.cache/1401/$name"
    fi
fi

if [ -z "$zip" ] || [ ! -f "$zip" ]; then
    echo "OpenCore release archive not found." >&2
    echo "Set OPENCORE_ZIP to the OpenCore-<version>-{DEBUG,RELEASE}.zip the EFI was built from," >&2
    echo "or put it in ~/.cache/1401/ (1401 keeps it there after a build)." >&2
    exit 2
fi

ver=$(basename "$zip" | sed -nE 's/^OpenCore-([0-9.]+)-(DEBUG|RELEASE)\.zip$/\1/p')
[ -n "$ver" ] || { echo "cannot read the OpenCore version from $(basename "$zip")" >&2; exit 2; }

# The config is only this release's config if the boot files came from this release.
for rel in OC/OpenCore.efi BOOT/BOOTx64.efi; do
    want=$(unzip -p "$zip" "X64/EFI/$rel" | sha256sum | cut -d' ' -f1)
    got=$(sha256sum "$efi/$rel" | cut -d' ' -f1)
    if [ "$want" != "$got" ]; then
        echo "MISMATCH: $efi/$rel and $(basename "$zip") are not the same file." >&2
        echo "  EFI:     $got" >&2
        echo "  archive: $want" >&2
        echo "Find the archive this EFI was built from; do not validate with a different release." >&2
        exit 1
    fi
done

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
unzip -p "$zip" Utilities/ocvalidate/ocvalidate.linux > "$tmp/ocvalidate.linux"
chmod +x "$tmp/ocvalidate.linux"

echo "OpenCore $ver  ($(basename "$zip"))"
"$tmp/ocvalidate.linux" "$cfg"
