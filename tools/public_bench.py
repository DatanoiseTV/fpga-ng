#!/usr/bin/env python3
"""Compare two nextpnr-ecp5 binaries on a folder of synthesised designs and print a table that can be pasted into an
issue or pull request.

For every <name>.json in the designs folder it runs both binaries for each seed with identical arguments and reports the
median router time, the median CPU time of the whole run (user + system, from getrusage) and the achieved Fmax of every
clock after routing. An optional <name>.lpf next to the json is passed as --lpf. Extra nextpnr arguments for all runs
can be given after "--", for example the device:

    ./public_bench.py --baseline ./nextpnr-ecp5-upstream --candidate ./nextpnr-ecp5-branch \
        --designs designs --seeds 1,2,3,4,5 -- --45k --package CABGA381 --speed 6 --freq 100 --timing-allow-fail

Runs that fail or do not finish within --timeout seconds are listed as such. Fmax values are a function of the target
frequency, so use the same one for both binaries (the script does).
"""
import argparse
import os
import re
import resource
import statistics
import subprocess
import sys
import time


def run_once(binary, design, lpf, seed, extra, timeout):
    cmd = [binary, "--json", design, "--seed", str(seed), "--textcfg", os.devnull] + extra
    if lpf:
        cmd += ["--lpf", lpf]
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"status": "timeout"}
    wall = time.time() - t0
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
    log = p.stdout + p.stderr
    if p.returncode != 0:
        return {"status": "exit %d" % p.returncode}
    router = re.search(r"Router[12] time ([\d.]+)s", log)
    fmax = {}
    for m in re.finditer(r"Max frequency for clock\s+'([^']+)': ([\d.]+) MHz", log):
        fmax[m.group(1)] = float(m.group(2))  # the last one printed is the post-route value
    return {"status": "ok", "wall": wall, "cpu": cpu, "router": float(router.group(1)) if router else None, "fmax": fmax}


def summarise(runs):
    ok = [r for r in runs if r["status"] == "ok"]
    bad = [r["status"] for r in runs if r["status"] != "ok"]
    out = {"n": len(ok), "bad": bad}
    if not ok:
        return out
    out["cpu"] = statistics.median(r["cpu"] for r in ok)
    routers = [r["router"] for r in ok if r["router"] is not None]
    out["router"] = statistics.median(routers) if routers else None
    clocks = sorted({c for r in ok for c in r["fmax"]})
    out["fmax"] = {c: [r["fmax"][c] for r in ok if c in r["fmax"]] for c in clocks}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--designs", required=True, help="folder with <name>.json (and optional <name>.lpf)")
    ap.add_argument("--seeds", default="1,2,3")
    ap.add_argument("--timeout", type=int, default=1800, help="seconds per run")
    ap.add_argument("extra", nargs="*", help="extra nextpnr arguments, after --")
    a = ap.parse_args()
    seeds = [int(s) for s in a.seeds.split(",")]
    designs = sorted(f[:-5] for f in os.listdir(a.designs) if f.endswith(".json"))
    print("| design | binary | runs ok | router time (s) | CPU time (s) | Fmax per clock, median / best (MHz) |")
    print("|---|---|---|---|---|---|")
    for d in designs:
        path = os.path.join(a.designs, d + ".json")
        lpf = os.path.join(a.designs, d + ".lpf")
        lpf = lpf if os.path.exists(lpf) else None
        for label, binary in (("baseline", a.baseline), ("candidate", a.candidate)):
            s = summarise([run_once(binary, path, lpf, seed, a.extra, a.timeout) for seed in seeds])
            if s["n"] == 0:
                print("| %s | %s | 0/%d (%s) | | | |" % (d, label, len(seeds), ", ".join(s["bad"])))
                continue
            fm = "; ".join("%s %.1f / %.1f" % (re.sub(r"^\$glbnet\$|\$TRELLIS_IO_IN$", "", c), statistics.median(v), max(v))
                           for c, v in s["fmax"].items())
            bad = (" (" + ", ".join(s["bad"]) + ")") if s["bad"] else ""
            print("| %s | %s | %d/%d%s | %s | %.1f | %s |" % (
                d, label, s["n"], len(seeds), bad, "%.1f" % s["router"] if s["router"] is not None else "-", s["cpu"], fm))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
