#!/usr/bin/env bash
#
# Fail when the turbidity sampler stops fitting the board, the clear tube, its screws, their drivers,
# the actuator, the riser or the o-rings of the foot.
#
# tests/sampler-case/fit.scad draws each fit check as the material that should not exist, so the
# check passes only when the render is EMPTY, and OpenSCAD then writes no file. Runs as
# `just check-sampler-case`.
set -uo pipefail
: "${OPENSCAD:=openscad}"
# A binary that cannot render anything also reports "nothing rendered".
source "$(dirname "$0")/openscad-canary.sh"
openscad_canary
tmp=$(mktemp -d) && trap 'rm -rf "$tmp"' EXIT
"$OPENSCAD" -o "$tmp/fit.stl" tests/sampler-case/fit.scad 2>"$tmp/err" >/dev/null
if grep -qE '^(ERROR|WARNING)|Assertion' "$tmp/err"; then
    echo "FAIL  sampler fits did not render"; grep -m3 -E '^(ERROR|WARNING)|Assertion' "$tmp/err" | sed 's/^/        /'; exit 1
elif [ -f "$tmp/fit.stl" ]; then
    echo "FAIL  sampler fits: something stands where it must not; render tests/sampler-case/fit.scad to see it"; exit 1
fi
echo "ok    sampler fits the board, the clear tube, its screws, their drivers, the actuator, the riser and its o-rings"
