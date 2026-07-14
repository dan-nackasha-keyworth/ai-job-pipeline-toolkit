#!/usr/bin/env python3
"""
Reproducible check for the recalibration agent's underlying computation
(SKILL.md, Step 6) against whatever is currently in examples/applications/.

This is the mechanical, non-LLM part of the recalibration agent – reading
logged outcomes and computing per-component positive/negative score means.
Making this a real script (not a one-off calculation in TESTING.md) means
it's re-verified on every push via CI, not just checked once by hand.

The LLM-interpreted parts of SKILL.md (actual scoring, live-search
verification) aren't reproducible this way – they need an independent
Claude session run, not a script. See TESTING.md for what this does and
doesn't prove.

Run from the repo root: python scripts/verify_recalibration.py
Exits 1 if the gate no longer passes against the current example data, so a
future edit to examples/ that breaks the demo's own premise gets caught.
"""
import json
import math
import os
import re
import statistics
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _status import recalibration_signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS_DIR = os.path.join(ROOT, "examples", "applications")
WEIGHTS_PATH = os.path.join(ROOT, "config", "weights.json")

COMPONENTS = ["jd_fit", "seniority", "competition", "comp", "blockers"]


def standardize(matrix):
    """Z-score each column. Returns (standardized matrix, means, stds)."""
    n = len(matrix)
    p = len(matrix[0])
    means = [sum(row[j] for row in matrix) / n for j in range(p)]
    stds = []
    for j in range(p):
        var = sum((row[j] - means[j]) ** 2 for row in matrix) / n
        stds.append(var ** 0.5 if var > 0 else 1.0)
    standardized = [[(row[j] - means[j]) / stds[j] for j in range(p)] for row in matrix]
    return standardized, means, stds


def sigmoid(z):
    # Numerically stable form – avoids overflow on large |z|.
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    ez = math.exp(z)
    return ez / (1.0 + ez)


def fit_logistic_regression(X, y, l2=1.0, lr=0.3, iters=3000):
    """
    Plain-gradient-descent logistic regression with L2 (ridge) regularisation,
    no external dependencies. L2 matters here specifically because n is small
    relative to the 5 features – without it, coefficients on a handful of
    dozens of outcomes can swing wildly. Features must already be standardized
    (see standardize()) so coefficient magnitudes are comparable to each other.
    """
    n = len(X)
    p = len(X[0])
    coefs = [0.0] * p
    intercept = 0.0
    for _ in range(iters):
        grad_coefs = [0.0] * p
        grad_intercept = 0.0
        for i in range(n):
            z = intercept + sum(coefs[j] * X[i][j] for j in range(p))
            err = sigmoid(z) - y[i]
            grad_intercept += err
            for j in range(p):
                grad_coefs[j] += err * X[i][j]
        grad_intercept /= n
        for j in range(p):
            grad_coefs[j] = grad_coefs[j] / n + (l2 * coefs[j] / n)
        intercept -= lr * grad_intercept
        for j in range(p):
            coefs[j] -= lr * grad_coefs[j]
    return intercept, coefs


def load_applications():
    apps = []
    for fname in sorted(os.listdir(APPS_DIR)):
        if not fname.endswith(".md"):
            continue
        text = open(os.path.join(APPS_DIR, fname), encoding="utf-8").read()
        fm = yaml.safe_load(re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL).group(1))
        apps.append(fm)
    return apps


def main():
    weights = json.load(open(WEIGHTS_PATH, encoding="utf-8"))
    min_logged = weights["recalibration"]["min_logged_outcomes"]
    min_positive = weights["recalibration"]["min_positive_outcomes"]
    min_logged_joint = weights["recalibration"].get("min_logged_outcomes_joint", min_logged)

    apps = load_applications()
    signals = [(a, recalibration_signal(a["status"])) for a in apps]
    logged_signals = [(a, sig) for a, sig in signals if sig is not None]
    logged = [a for a, sig in logged_signals]
    positive = [a for a, sig in logged_signals if sig == "positive"]
    negative = [a for a, sig in logged_signals if sig == "negative"]

    gate_passes = len(logged) >= min_logged and len(positive) >= min_positive

    print(f"Total applications: {len(apps)}")
    print(f"Logged outcomes: {len(logged)} (threshold: {min_logged})")
    print(f"Positive outcomes: {len(positive)} (threshold: {min_positive})")
    print(f"Gate: {'PASS' if gate_passes else 'BELOW THRESHOLD'}")
    print()

    no_variance = []
    for c in COMPONENTS:
        pos_vals = [a["score"]["breakdown"][c] for a in positive]
        neg_vals = [a["score"]["breakdown"][c] for a in negative]
        all_vals = pos_vals + neg_vals
        pos_mean = statistics.mean(pos_vals) if pos_vals else float("nan")
        neg_mean = statistics.mean(neg_vals) if neg_vals else float("nan")
        variance_flag = " (NO VARIANCE – agent has zero signal here)" if len(set(all_vals)) <= 1 else ""
        if variance_flag:
            no_variance.append(c)
        print(f"{c:12s} positive mean={pos_mean:5.1f}  negative mean={neg_mean:5.1f}  diff={pos_mean - neg_mean:+5.1f}{variance_flag}")

    print()
    if no_variance:
        print(f"Components with no variance in example data: {', '.join(no_variance)}")
    else:
        print("All five components have variance across the example data – the recalibration agent has some signal on every component.")

    print()
    print(f"Joint model (logistic regression, L2-regularised) – threshold {min_logged_joint} logged outcomes:")
    if len(logged) < min_logged_joint:
        print(f"  BELOW THRESHOLD – have {len(logged)}, need {min_logged_joint}. A joint model needs proportionally "
              f"more data than the single-component means above to avoid unstable coefficients; not shown.")
    else:
        X_raw = [[a["score"]["breakdown"][c] for c in COMPONENTS] for a, sig in logged_signals]
        y = [1 if sig == "positive" else 0 for a, sig in logged_signals]
        X, means, stds = standardize(X_raw)
        intercept, coefs = fit_logistic_regression(X, y)
        ranked = sorted(zip(COMPONENTS, coefs), key=lambda t: -abs(t[1]))
        print("  Standardised coefficients (larger magnitude = stronger association with a positive outcome,")
        print("  holding the other four components constant – this is what the per-component means above cannot show):")
        for name, coef in ranked:
            print(f"    {name:12s} {coef:+.3f}")
        print("  Same caveat as the per-component means: a weak signal from a small sample, not a validated finding.")

    if not gate_passes:
        print("\nFAIL: example dataset no longer crosses the recalibration gate threshold.")
        sys.exit(1)


if __name__ == "__main__":
    main()
