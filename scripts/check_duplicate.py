#!/usr/bin/env python3
"""
Checks whether a company+role combination likely already exists among
tracked applications, before SKILL.md Step 2 creates a new one.

Deliberately simple matching, not fuzzy NLP - two tiers, both advisory,
neither ever blocks anything:

- Same company (normalized: lowercased, legal suffixes and punctuation
  stripped) AND the same role title after the same normalization -> HIGH
  confidence match. Likely an accidental duplicate paste, or the same
  listing reposted under an identical title.
- Same company, but a DIFFERENT role title -> LOW confidence match, flagged
  separately and more gently. Two genuinely distinct roles at the same
  company (a real, common pattern - see TESTING.md Test 20) must never be
  silently treated as the same one just because the company matches. This
  tier exists to prompt a quick "is this the same role or a new one?"
  question, not to accuse.

No fuzzy/partial title matching is attempted on purpose - substring or
similarity-score matching on job titles is a fast route to false positives
("Head of Product" matching "Head of Product Strategy", a genuinely
different role). Exact-after-normalization is a deliberately narrow, honest
tool: it catches true duplicates and true reposts, and says plainly when it
can't tell, rather than guessing.

Run from the repo root (checks examples/applications/ by default), or point
--dir at a real user's own applications folder:

  python scripts/check_duplicate.py --company "Acme Corp" --role "Head of Product"
  python scripts/check_duplicate.py --company "Acme Corp" --role "Head of Product" --dir path/to/applications

Always exits 0 - this is advisory output for SKILL.md Step 2 to relay to
the user, never a gate.
"""
import argparse
import os
import re

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DIR = os.path.join(ROOT, "examples", "applications")

LEGAL_SUFFIXES = re.compile(
    r"\b(inc|incorporated|ltd|limited|llc|llp|plc|corp|corporation|co|company|gmbh|sa|ag)\.?\b",
    re.IGNORECASE,
)


def normalize(text):
    text = text.lower().strip()
    text = LEGAL_SUFFIXES.sub("", text)
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_applications(directory):
    apps = []
    if not os.path.isdir(directory):
        return apps
    for fname in sorted(os.listdir(directory)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(directory, fname)
        text = open(path, encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if not m:
            continue
        fm = yaml.safe_load(m.group(1))
        apps.append({
            "fname": fname,
            "company": fm.get("company", ""),
            "role": fm.get("role", ""),
            "status": fm.get("status", ""),
            "date_scored": fm.get("date_scored"),
        })
    return apps


def find_matches(company, role, directory):
    company_norm = normalize(company)
    role_norm = normalize(role)
    high, low = [], []
    for app in load_applications(directory):
        if normalize(app["company"]) != company_norm:
            continue
        if normalize(app["role"]) == role_norm:
            high.append(app)
        else:
            low.append(app)
    return high, low


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--company", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--dir", default=DEFAULT_DIR)
    args = parser.parse_args()

    high, low = find_matches(args.company, args.role, args.dir)

    if not high and not low:
        print(f"No existing tracked application found for {args.company!r} / {args.role!r}.")
        return

    if high:
        print(f"HIGH confidence match - same company and same role title already tracked:")
        for app in high:
            print(f"  {app['fname']}  (status: {app['status']}, scored: {app['date_scored']})")
        print("Likely an accidental duplicate, or this exact listing reposted. Confirm with the user before creating a new file rather than silently doing so.")

    if low:
        print(f"LOW confidence match - {args.company!r} already has {len(low)} other tracked application(s) under a different role title:")
        for app in low:
            print(f"  {app['fname']}  -> {app['role']!r} (status: {app['status']})")
        print("Could be a genuinely distinct role, or the same one under a reworded title. Ask, don't assume either way.")


if __name__ == "__main__":
    main()
