#!/usr/bin/env bash
# Validate an EFI with 1401's own validator path, not a reimplementation:
#
#   p1401/validate.py:_opencore_release()   reads OCK_Files/history.json -> OpenCorePkg url + sha256
#   p1401/validate.py:ocvalidate_path()     verifies the archive sha, extracts
#                                           Utilities/ocvalidate/ocvalidate.linux, verifies its bytes
#   p1401/validate.py:release_components()  proves EFI/BOOT/BOOTx64.efi, EFI/OC/OpenCore.efi and the
#                                           enabled drivers are byte-identical to that archive
#   p1401/validate.py:run_ocvalidate()      runs it
#
#   scripts/ocvalidate-efi.sh <efi-dir> [config.plist]
#
# The 1401 checkout must be at .reference/1401 (docs/reference.md). If the archive is not in
# ~/.cache/1401 yet, 1401's code downloads and verifies the release it recorded.
set -euo pipefail

efi=$(cd "${1:?usage: scripts/ocvalidate-efi.sh <efi-dir> [config.plist]}" && pwd)
cfg=${2:-$efi/EFI/OC/config.plist}
root=$(cd "$(dirname "$0")/.." && pwd)
repo="$root/.reference/1401"

[ -f "$cfg" ] || { echo "no config at $cfg" >&2; exit 2; }
[ -d "$repo/p1401" ] || { echo "1401 checkout missing at $repo (see docs/reference.md)" >&2; exit 2; }

cd "$repo"
python3 - "$efi" "$cfg" <<'PY'
import sys

from p1401 import validate

efi, cfg = sys.argv[1], sys.argv[2]

try:
    ok, issues, text = validate.run_ocvalidate(cfg)   # ensures the archive is cached and verified
except Exception as error:
    print("validator unavailable: %s: %s" % (type(error).__name__, error), file=sys.stderr)
    raise SystemExit(2)

url, sha = validate._opencore_release()
print("OpenCore release: %s  sha256 %s..." % (url.rsplit("/", 1)[-1], sha[:12]))

failures = validate.release_components(efi)
if failures:
    print("EFI does not match that OpenCore release:", file=sys.stderr)
    for failure in failures:
        print("  - " + failure, file=sys.stderr)
    raise SystemExit(1)

print(text)
raise SystemExit(0 if ok else 1)
PY
