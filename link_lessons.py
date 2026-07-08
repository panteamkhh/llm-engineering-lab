#!/usr/bin/env python3
"""
link_lessons.py
----------------
Walks the repo, finds every docs/*.md file inside each lesson folder,
and turns plain-text references like:

    "Lesson 07"
    "Lessons 03-04"
    "Lessons 03–04"        (en-dash)
    "Lessons 01–09"
    "Lessons 03-04, 07"
    "درس 07"

into real markdown links pointing at that lesson's folder on GitHub, e.g.:

    "(see Lesson 07)"
 -> "(see [Lesson 07](https://github.com/panteamkhh/llm-engineering-lab/tree/main/07-search-apps-and-vector-databases))"

Each number inside a range/list is linked individually:

    "(see Lessons 03-04, 07)"
 -> "(see Lessons [03](.../03-prompt-engineering-fundamentals)-[04](.../04-advanced-prompt-engineering), [07](.../07-search-apps-and-vector-databases))"

Usage (run from the REPO ROOT, e.g. D:\\LLM Engineering Lab):
    python3 link_lessons.py            # writes changes
    python3 link_lessons.py --dry-run  # only prints what WOULD change
"""

import argparse
import os
import re

# Base GitHub repo URL — edit if the repo moves.
REPO_URL = "https://github.com/panteamkhh/llm-engineering-lab/tree/main"

# number -> folder name (from README.md roadmap table)
LESSON_FOLDERS = {
    1: "01-foundations-of-generative-ai-and-llms",
    2: "02-responsible-generative-ai",
    3: "03-prompt-engineering-fundamentals",
    4: "04-advanced-prompt-engineering",
    5: "05-building-text-generation-apps",
    6: "06-building-chat-applications",
    7: "07-search-apps-and-vector-databases",
    8: "08-building-image-generation-apps",
    9: "09-low-code-function-calling-and-ux",
    10: "10-security-lifecycle-agents-and-fine-tuning",
}

DOCS_SUBDIR = "docs"

# --- Regex machinery -------------------------------------------------
# A single lesson number: optional leading zero + 1-2 digits.
NUM = r"0?\d{1,2}"
# Separator between numbers in a list/range: "-", "–", "—", ",", "and", "&"
SEP = r"(?:\s*[-\u2013\u2014,]\s*|\s+and\s+|\s*&\s*)"
# One or more numbers chained by separators: "07" / "03-04" / "03-04, 07" / "01-09"
NUMLIST = rf"{NUM}(?:{SEP}{NUM})*"

# "Lesson"/"Lessons"/"درس" + whitespace + a numlist, as its own capture groups
PATTERN = re.compile(
    rf"(?P<label>Lessons?|درس)(?P<ws>\s+)(?P<numlist>{NUMLIST})\b",
    re.IGNORECASE,
)

SINGLE_NUM = re.compile(r"\d{1,2}")


def target_url_for(num: int) -> str | None:
    """Return the GitHub folder URL for lesson `num`, or None if unknown."""
    folder = LESSON_FOLDERS.get(num)
    if not folder:
        return None
    return f"{REPO_URL}/{folder}"


def already_linked(text: str, start: int, end: int) -> bool:
    """True if the match is already wrapped as a markdown link, e.g.
    [Lesson 07](...). Range/list matches are naturally idempotent because
    once a number is replaced with [07](...), a re-run's numlist pattern
    (which requires digits right after 'Lesson(s)') no longer matches."""
    before = text[:start]
    after = text[end:]
    if before.endswith("["):
        return True
    if after.startswith("]("):
        return True
    return False


def process_file(filepath: str, current_num: int | None, dry_run: bool) -> int:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    changes = 0

    def replace_number(match: re.Match) -> str:
        nonlocal changes
        num = int(match.group(0))
        if num == current_num:
            return match.group(0)  # don't self-link
        url = target_url_for(num)
        if not url:
            return match.group(0)  # unknown lesson number, leave as-is
        changes += 1
        return f"[{match.group(0)}]({url})"

    def replacer(match: re.Match) -> str:
        if already_linked(content, match.start(), match.end()):
            return match.group(0)
        label = match.group("label")
        ws = match.group("ws")
        numlist = match.group("numlist")
        new_numlist = SINGLE_NUM.sub(replace_number, numlist)
        return f"{label}{ws}{new_numlist}"

    new_content = PATTERN.sub(replacer, content)

    if changes and not dry_run:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

    if changes:
        print(f"{'[dry-run] ' if dry_run else ''}{filepath}: {changes} link(s)")

    return changes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview only, don't write files")
    parser.add_argument("--root", default=".", help="Repo root (default: current dir)")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.root)
    total = 0

    for num, folder in LESSON_FOLDERS.items():
        docs_dir = os.path.join(repo_root, folder, DOCS_SUBDIR)
        if not os.path.isdir(docs_dir):
            continue
        for fname in os.listdir(docs_dir):
            if fname.endswith(".md"):
                fpath = os.path.join(docs_dir, fname)
                total += process_file(fpath, num, args.dry_run)

    print(f"\nDone. {total} link(s) {'would be ' if args.dry_run else ''}created.")


if __name__ == "__main__":
    main()
