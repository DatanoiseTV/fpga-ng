# fpga-ng

Test tools, benchmark designs and notes for a few nextpnr pull requests about run time and clock speed on ECP5, mostly
for the Colorlight i9 (ECP5-45F). The code is in the PRs; this repository is where the benchmarking lives so that other
people can run the same comparison on their own designs and devices.

**Status: draft pull requests, looking for testers.** Everything here was measured on an ECP5-45F only, mostly on an
Apple M5 Pro. I would like to know how it behaves on the 25F and 85F, on other designs, and on Linux.

## The pull requests

All against [YosysHQ/nextpnr](https://github.com/YosysHQ/nextpnr), opened as drafts. The branches are in
[DatanoiseTV/nextpnr](https://github.com/DatanoiseTV/nextpnr).

| PR | Branch | What it is | Changes results? |
|---|---|---|---|
| [#1826](https://github.com/YosysHQ/nextpnr/pull/1826) `--setting` option | `pr/setting-option` | Override internal settings (router and placer tunables) from the command line | no |
| [#1827](https://github.com/YosysHQ/nextpnr/pull/1827) router1 on congested ECP5 designs | `pr/router1-congestion` | Bounded A* search, rip up only the arcs through a conflicting wire, a capped penalty for ripping up shared wires, a diagnostic that lists the nets with the most search work, enabled by default on ECP5 | yes, ECP5 only |
| [#1828](https://github.com/YosysHQ/nextpnr/pull/1828) placer speedups | `pr/placer-perf` | HeAP and SA stop recomputing things that did not change | no, bit-identical |
| [#1829](https://github.com/YosysHQ/nextpnr/pull/1829) `NDEBUG` in Release | `pr/release-ndebug` | The CMake Release flags drop `-DNDEBUG`, so debug checks run in release builds | no |

The router2 abort on ECP5 designs with a promoted global clock is already proposed upstream in #1824 (issue #1823),
so there is no PR from here for it; I confirmed it on a 45F there.

## Help test

1. Build the branch you want to try next to a build of current `main` (the PR pages say what they need).
2. Create the public benchmark designs, or use your own: `tools/make_designs.sh` builds six and eight PicoRV32 cores and
   a LiteX SoC for the i9 (needs yosys, Python 3.10 for LiteX, and a network connection).
3. Compare the two binaries:

   ```
   tools/public_bench.py --baseline ./nextpnr-ecp5-main --candidate ./nextpnr-ecp5-branch \
       --designs designs --seeds 1,2,3,4,5 -- --45k --package CABGA381 --speed 6 --freq 100 --timing-allow-fail
   ```

   It prints a markdown table (router time, CPU time, Fmax per clock). Use your own device flags after `--`.
4. For the changes that are meant to be pure speedups, check that the results really are identical:
   `tools/checksum_check.sh <main> <branch> 1,2,3 designs/<x>.json <device flags>`.
5. Paste the table, the device, the OS and the compiler into a comment on the PR.

The designs I most want to hear about are the ones where router1 takes minutes. Run them with
`--setting router1/reportHeavyNets=5` on the router branch and look at the list at the end: if a single net
accounts for most of the A* node visits, that is the case the router PR is about.

## What was measured

Public designs, 5 seeds, ECP5-45F, `--freq 100`, versus current main (macOS arm64, Apple clang, medians):

| design | router branch: router time | placer branch: CPU time | Fmax |
|---|---|---|---|
| LiteX i9 SoC (VexRiscv, Ethernet; 8.4k LUT4) | 9.7 s to 7.9 s | 19.5 s to 17.2 s | unchanged |
| 6x PicoRV32 (25k LUT4) | 17.4 s to 16.7 s | 65.6 s to 56.9 s | unchanged |
| 8x PicoRV32 (33k LUT4) | 25.8 s to 24.9 s | 90.1 s to 71.1 s | unchanged |

Full tables are in `results/`. On these designs the router change is small. The case it was written for, a LiteX SoC
of about 20k LUT4 and 91k arcs, I cannot share: there router1 took 731 s on seed 1, the same seed takes 34 s with the new options, and five
other seeds take 21-26 s, with Fmax in the same range. I could not build a public design that shows that (the two attempts are in
`designs-src/`: a big enable net next to routable logic is fine for both versions, a randomly cross-coupled one cannot be
routed by either).

## Things that did not work

These come from two ECP5-45F designs I cannot share, so treat them as observations, not results:

- A GPU is not a fit: the designs are too small for a launch to pay, and the router's search is irregular.
- router2 is much faster on the large design but reached about 10-15% lower Fmax than router1, and none of its
  parameters, a post-routing delay polish, or attaching arcs to the existing route tree closed that gap (each moved the
  median by about 2 MHz, which is inside seed noise).
- The post-placement Fmax estimate hardly predicts the post-routing Fmax (rank correlation 0.11 over 16 seeds), so
  "place many seeds, route only the best" does not work.
- Different Yosys synthesis options: `-abc9` is already the default, `-retime` is incompatible with it, `-nowidelut`
  lowered Fmax.
- Handing over to router2 when router1 stalls gave lower Fmax than either router alone.

## Layout

- `tools/public_bench.py`: compare two binaries on a folder of designs.
- `tools/checksum_check.sh`: check two binaries give identical results.
- `tools/make_designs.sh`, `designs-src/`: the public designs.
- `results/`: the tables quoted above.

The scripts use only the standard library and bash. ISC licensed, like nextpnr.
