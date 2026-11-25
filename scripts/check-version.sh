#!/usr/bin/env bash
#
# Fail unless the version is the same everywhere it is written: CMakeLists.txt's project(),
# library.json, CITATION.cff and the newest released section of CHANGELOG.md. On a tag, it must
# also be the tag's version, so a release cannot ship metadata that names another.
# Runs in `just check`.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

cmake=$(sed -n 's/^project(turbidity VERSION \([0-9][0-9.]*\).*/\1/p' CMakeLists.txt)
library=$(sed -n 's/^ *"version": *"\([^"]*\)".*/\1/p' library.json | head -1)
citation=$(sed -n 's/^version: *"\{0,1\}\([^"]*\)"\{0,1\} *$/\1/p' CITATION.cff)
changelog=$(sed -n 's/^## \[\([0-9][0-9.]*\)\].*/\1/p' CHANGELOG.md | head -1)

# The tag being built: CI sets GITHUB_REF_TYPE and GITHUB_REF_NAME; locally, a tag on HEAD.
tag=""
if [ "${GITHUB_REF_TYPE:-}" = "tag" ]; then
    tag=${GITHUB_REF_NAME:-}
elif [ -z "${GITHUB_ACTIONS:-}" ]; then
    tag=$(git describe --exact-match --tags HEAD 2>/dev/null || true)
fi
tag=${tag#v}

fail=0
for pair in "CMakeLists.txt:$cmake" "library.json:$library" "CITATION.cff:$citation" \
    "CHANGELOG.md:$changelog"; do
    if [ -z "${pair#*:}" ]; then
        echo "FAIL  version: no version found in ${pair%%:*}"
        fail=1
    fi
done
[ "$fail" = 0 ] || exit 1

if [ "$cmake" != "$library" ] || [ "$cmake" != "$citation" ] || [ "$cmake" != "$changelog" ]; then
    echo "FAIL  version: CMakeLists.txt $cmake, library.json $library, CITATION.cff $citation," \
        "CHANGELOG.md's newest release $changelog"
    exit 1
fi
if [ -n "$tag" ] && [ "$tag" != "$cmake" ]; then
    echo "FAIL  version: the tag is v$tag but the metadata says $cmake"
    exit 1
fi
where="CMakeLists.txt, library.json, CITATION.cff and CHANGELOG.md"
[ -n "$tag" ] && where="$where, and the tag"
echo "ok    version $cmake in $where"
