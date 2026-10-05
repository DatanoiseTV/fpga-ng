#!/bin/bash
# Check that two nextpnr binaries produce exactly the same result: nextpnr prints a checksum of the design after packing,
# placement and routing ("Checksum: 0x..."), and for a change that is meant to be a pure speedup all three must match.
#
# usage: checksum_check.sh <baseline> <candidate> <seeds, comma separated> <design.json> [nextpnr arguments...]
#   e.g. checksum_check.sh ./nextpnr-ecp5-upstream ./nextpnr-ecp5-branch 1,2,3 designs/picorv32_x6.json \
#            --45k --package CABGA381 --speed 6 --freq 100 --timing-allow-fail
# Both sides get identical arguments. Note that adding options such as --setting or --threads changes even the checksum
# after packing, so only compare runs that use the same options.
base=$1; cand=$2; seeds=$3; design=$4; shift 4
fail=0
for s in ${seeds//,/ }; do
  a=$("$base" --json "$design" --seed "$s" --textcfg /dev/null "$@" 2>&1 | grep Checksum | tr '\n' ' ')
  b=$("$cand" --json "$design" --seed "$s" --textcfg /dev/null "$@" 2>&1 | grep Checksum | tr '\n' ' ')
  if [ -n "$a" ] && [ "$a" == "$b" ]; then echo "seed $s: identical ($a)"; else echo "seed $s: DIFFERENT"; echo "  baseline:  $a"; echo "  candidate: $b"; fail=1; fi
done
exit $fail
