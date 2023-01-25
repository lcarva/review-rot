#!/bin/bash
set -euo pipefail

output="$1"

authors='[
  "cuipinghuo",
  "joejstuart",
  "lcarva",
  "robnester-rh",
  "simonbaird",
  "zregvart",
  "ec-automation[bot]"
]'

config=$(mktemp)
trap "rm ${config}" EXIT

< examples/enterprise.yaml envsubst > ${config}
review-rot -c ${config} | \
    jq --argjson authors "${authors}" -r '[.[] | select(([.user] | inside($authors)) or (.url | contains("/hacbs-contract/")) or (.title | test("enterprise.contract"; "i")) )]' > ${output}
