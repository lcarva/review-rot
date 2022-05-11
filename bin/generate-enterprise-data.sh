#!/bin/bash
set -euo pipefail

output="$1"

authors="$(
echo '
  bcaton85
  caugello
  cuipinghuo
  joejstuart
  kbenoit-rh
  lcarva
  robnester-rh
  simonbaird
  zregvart
' | xargs | jq -c -R '. | split(" ")')"

config=$(mktemp)
trap "rm ${config}" EXIT

< examples/enterprise.yaml envsubst > ${config}
review-rot -c ${config} | \
    jq -r '[.[] | select([.user] | inside('${authors}'))]' > ${output}
