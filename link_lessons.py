#!/usr/bin/env python3
"""
link_lessons.py
----------------
Walks the repo, finds every docs/*.md file inside each lesson folder,
and turns plain-text references like "Lesson 07" / "lesson 7" / "درس 07"
into real markdown links pointing at that lesson's doc file
(same language file when it exists, otherwise falling back to en.md).

Usage (run from the REPO ROOT):
    python3 link_lessons.py            # writes changes
    python3 link_lessons.py --dry-run  # only prints what WOULD change
"""

import argparse
import os
import re

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
FALLBACK_LANG_FILE = "en.md"

# Matches "Lesson 7", "lesson07", "Lesson 07", and Persian "درس 07"
PATTERN = re.compile(r"(?P<label>Lesson|lesson|درس)\s*0?(?P<num>\d{1,2})\b")


def target_file_for(num: int, lang_filename: str, repo_root: str) -> str | None:
    """Return the docs file to link to for lesson `num`, preferring the same
    language file as the current doc, falling back to en.md."""
    folder = LESSON_FOLDERS.get(num)
    if not folder:
        return None
    docs_dir = os.path.join(repo_root, folder, DOCS_SUBDIR)
    same_lang = os.path.join(docs_dir, lang_filename)
    if os.path.isfile(same_lang):
        return same_lang
    fallback = os.path.join(docs_dir, FALLBACK_LANG_FILE)
    if os.path.isfile(fallback):
        return fallback
    return None


def already_linked(text: str, start: int, end: int) -> bool:
    """True if the match is already inside a markdown link, e.g. [Lesson 07](...)."""
    before = text[:start]
    after = text[end:]
    if before.endswith("["):
        return True
    if after.startswith("]("):
        return True
    return False


def process_file(filepath: str, repo_root: str, dry_run: bool) -> int:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lang_filename = os.path.basename(filepath)  # e.g. en.md / fa.md
    current_folder = os.path.basename(os.path.dirname(os.path.dirname(filepath)))
    current_num = next(
        (n for n, folder in LESSON_FOLDERS.items() if folder == current_folder), None
    )

    changes = 0

    def replacer(match: re.Match) -> str:
        nonlocal changes
        if already_linked(content, match.start(), match.end()):
            return match.group(0)

        num = int(match.group("num"))
        if num == current_num:
            return match.group(0)  # don't self-link

        target = target_file_for(num, lang_filename, repo_root)
        if not target:
            return match.group(0)  # unknown lesson number, leave as-is

        rel_path = os.path.relpath(target, os.path.dirname(filepath))
        rel_path = rel_path.replace(os.sep, "/")
        changes += 1
        return f"[{match.group(0)}]({rel_path})"

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
                total += process_file(fpath, repo_root, args.dry_run)

    print(f"\nDone. {total} link(s) {'would be ' if args.dry_run else ''}created.")


if __name__ == "__main__":
    main()
