#!/usr/bin/env python3
"""
Checks the most recent eval/results/*.json run against eval/expected_bands.json.

This is the mechanical half of the eval harness. It cannot run the scoring
itself - that's an LLM-interpreted step (see eval/README.md for how to
produce a new results file) - it only checks that a given results file's
scores fall within the pre-registered bands in expected_bands.json.

Run from the repo root: python scripts/verify_eval_results.py
Exits 1 if any component or total falls outside its expected band, or if a
golden-set case is missing from the results file.
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANDS_PATH = os.path.join(ROOT, "eval", "expected_bands.json")
RESULTS_DIR = os.path.join(ROOT, "eval", "results")

COMPONENTS = ["jd_fit", "seniority", "competition", "comp", "blockers"]


def latest_results_file():
    files = sorted(glob.glob(os.path.join(RESULTS_DIR, "*.json")))
    if not files:
        print("No results files found in eval/results/ - nothing to check.")
        print("See eval/README.md for how to produce one.")
        sys.exit(1)
    return files[-1]


def main():
    bands = json.load(open(BANDS_PATH, encoding="utf-8"))
    results_path = latest_results_file()
    results = json.load(open(results_path, encoding="utf-8"))

    print(f"Checking {os.path.basename(results_path)} against eval/expected_bands.json\n")

    bands_by_case = {c["case"]: c for c in bands["cases"]}
    results_by_case = {r["case"]: r for r in results["results"]}

    failures = []

    for case_name, case_bands in bands_by_case.items():
        if case_name not in results_by_case:
            failures.append(f"{case_name}: MISSING from results file")
            continue

        r = results_by_case[case_name]
        total = sum(r[c] for c in COMPONENTS)
        total_lo, total_hi = case_bands["total_band"]
        total_ok = total_lo <= total <= total_hi
        total_flag = "" if total_ok else "  <-- OUT OF BAND"
        print(f"{case_name}:")
        print(f"  total = {total:3d}  (expected {total_lo}-{total_hi}){total_flag}")
        if not total_ok:
            failures.append(f"{case_name}: total {total} outside expected band {total_lo}-{total_hi}")

        for c in COMPONENTS:
            lo, hi = case_bands["bands"][c]
            val = r[c]
            ok = lo <= val <= hi
            flag = "" if ok else "  <-- OUT OF BAND"
            print(f"    {c:12s} = {val:3d}  (expected {lo}-{hi}){flag}")
            if not ok:
                failures.append(f"{case_name}: {c} {val} outside expected band {lo}-{hi}")
        print()

    for case_name in results_by_case:
        if case_name not in bands_by_case:
            print(f"Note: {case_name} in results but not in expected_bands.json (not checked).")

    if failures:
        print(f"FAIL: {len(failures)} band violation(s):")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)

    print(f"PASS: all {len(bands_by_case)} golden-set cases fall within their expected bands.")


if __name__ == "__main__":
    main()
