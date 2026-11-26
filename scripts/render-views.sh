#!/usr/bin/env bash
#
# Render the rows of hardware/sampler-case/views.tsv to build/figures/<name>.png, cropped to the
# model. $1 is a glob over the names, "*" for all. Each render is an orthographic preview, so it
# takes seconds. A failing render still exits 0, so stderr is the signal.
set -uo pipefail
: "${OPENSCAD:=openscad}"
source "$(dirname "$0")/openscad-canary.sh"
openscad_canary
out=build/figures
mkdir -p "$out"
fail=0
while IFS=$'\t' read -r name view flags; do
    [[ -z "$name" || "$name" == \#* ]] && continue
    # shellcheck disable=SC2053
    [[ "$name" == ${1:-*} ]] || continue
    # A row asking for --render gets a full render: --preview anywhere on the line makes it a preview,
    # which draws every cut face in one colour.
    mode=--preview
    [[ " ${flags:-} " == *" --render "* ]] && mode=
    # shellcheck disable=SC2086
    "$OPENSCAD" $mode --projection=o --viewall --autocenter --camera="0,0,0,$view,0" \
        --imgsize=2400,1800 --colorscheme=Tomorrow ${flags:-} -o "$out/$name.png" \
        hardware/sampler-case/bayonet.scad 2>"$out/$name.err" >/dev/null
    if grep -q '^ERROR' "$out/$name.err" || [ ! -s "$out/$name.png" ]; then
        echo "FAIL  $name  see $out/$name.err"
        rm -f "$out/$name.png"
        fail=1
        continue
    fi
    bg=$(magick "$out/$name.png" -format '%[pixel:p{0,0}]' info:)
    magick "$out/$name.png" -fuzz 2% -trim +repage -bordercolor "$bg" -border 40 "$out/$name.png"
    rm -f "$out/$name.err"
    echo "ok    $name"
done < hardware/sampler-case/views.tsv
exit $fail
