#!/bin/bash
# Build the public benchmark designs used in the pull requests into ./designs (json + lpf, ready for public_bench.py).
#   - picorv32_x6, picorv32_x8: 6 and 8 PicoRV32 cores with a private 4 KB memory each, sharing clock and reset
#   - litex_i9_vexriscv: LiteX SoC for the Colorlight i9 (VexRiscv, Ethernet) generated from the public LiteX packages
# Needs: yosys on PATH, python3 and curl; for the LiteX design also python3.10 (Migen does not run on newer Pythons).
set -e
HERE=$(cd "$(dirname "$0")/.." && pwd)
OUT=${1:-$HERE/designs}
WORK=${WORK:-$HERE/work}
mkdir -p "$OUT" "$WORK"
cd "$WORK"

[ -f picorv32.v ] || curl -sL -o picorv32.v https://raw.githubusercontent.com/YosysHQ/picorv32/main/picorv32.v
for n in 6 8; do
  python3 "$HERE/designs-src/gen_stress.py" $n > stress_$n.v
  yosys -q -p "read_verilog -sv picorv32.v stress_$n.v; synth_ecp5 -top stress_top -json $OUT/picorv32_x$n.json"
  echo "built picorv32_x$n"
done

if command -v python3.10 > /dev/null; then
  [ -d litex-venv ] || { python3.10 -m venv litex-venv; ./litex-venv/bin/pip install --quiet litex litex-boards litedram liteeth litespi \
      pythondata-cpu-vexriscv pythondata-software-picolibc pythondata-software-compiler_rt; }
  rm -rf litex-out
  ./litex-venv/bin/python -m litex_boards.targets.colorlight_i5 --board i9 --revision 7.2 --cpu-type vexriscv \
      --cpu-variant full --with-ethernet --sys-clk-freq 50e6 --build --no-compile-software --no-compile-gateware \
      --output-dir litex-out > litex.log 2>&1
  (cd litex-out/gateware && yosys -q colorlight_i5.ys)
  cp litex-out/gateware/colorlight_i5.json "$OUT/litex_i9_vexriscv.json"
  cp litex-out/gateware/colorlight_i5.lpf "$OUT/litex_i9_vexriscv.lpf"
  echo "built litex_i9_vexriscv"
else
  echo "python3.10 not found: skipping the LiteX design"
fi
