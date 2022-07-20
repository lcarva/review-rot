#!/bin/bash
set -euo pipefail

output="$1"

authors='[
  "bcaton85",
  "caugello",
  "cuipinghuo",
  "joejstuart",
  "kbenoit-rh",
  "lcarva",
  "robnester-rh",
  "simonbaird",
  "zregvart"
]'

config=$(mktemp)
trap "rm ${config}" EXIT

< examples/enterprise.yaml envsubst > ${config}
review-rot -c ${config} | \
    jq --argjson authors "${authors}" -r '[.[] | select([.user] | inside($authors))]' > ${output}
