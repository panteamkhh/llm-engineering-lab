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

# Pass 1: an EXISTING markdown link whose visible text is "Lesson(s) NN" or
# just "NN", and whose target is a local-looking path (not already our
# GitHub URL). e.g. [Lesson 07](../../07-.../docs/en.md) or [07](../../07-.../docs/en.md)
EXISTING_LINK_PATTERN = re.compile(
    r"\[(?P<linktext>(?:Lessons?\s+)?0?\d{1,2})\]\((?P<url>[^)]+)\)",
    re.IGNORECASE,
)

# Pass 2: plain-text "Lesson"/"Lessons"/"درس" + whitespace + a numlist
PLAIN_TEXT_PATTERN = re.compile(
    rf"(?P<label>Lessons?|درس)(?P<ws>\s+)(?P<numlist>{NUMLIST})\b",
    re.IGNORECASE,
)

SINGLE_NUM = re.compile(r"\d{1,2}")
TRAILING_NUM = re.compile(r"\d{1,2}$")


def target_url_for(num: int) -> str | None:
    """Return the GitHub folder URL for lesson `num`, or None if unknown."""
    folder = LESSON_FOLDERS.get(num)
    if not folder:
        return None
    return f"{REPO_URL}/{folder}"


def looks_local(url: str) -> bool:
    """True if a URL looks like a local relative path rather than a real
    external link we should leave alone (e.g. already our GitHub URL)."""
    if url.startswith(REPO_URL):
        return False
    if url.startswith("http://") or url.startswith("https://"):
        return False  # some other real URL — don't touch it
    return True


def fix_existing_links(content: str, current_num: int | None) -> tuple[str, int]:
    changes = 0

    def replacer(match: re.Match) -> str:
        nonlocal changes
        linktext = match.group("linktext")
        url = match.group("url")
        if not looks_local(url):
            return match.group(0)

        m = TRAILING_NUM.search(linktext)
        if not m:
            return match.group(0)
        num = int(m.group(0))

        new_url = target_url_for(num)
        if not new_url or new_url == url:
            return match.group(0)

        changes += 1
        return f"[{linktext}]({new_url})"

    new_content = EXISTING_LINK_PATTERN.sub(replacer, content)
    return new_content, changes


def link_plain_text(content: str, current_num: int | None) -> tuple[str, int]:
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
        before = content[: match.start()]
        after = content[match.end() :]
        if before.endswith("["):
            return match.group(0)  # already inside a link, pass 1 handles it
        if after.startswith("]("):
            return match.group(0)

        label = match.group("label")
        ws = match.group("ws")
        numlist = match.group("numlist")
        new_numlist = SINGLE_NUM.sub(replace_number, numlist)
        return f"{label}{ws}{new_numlist}"

    new_content = PLAIN_TEXT_PATTERN.sub(replacer, content)
    return new_content, changes


def process_file(filepath: str, current_num: int | None, dry_run: bool) -> int:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    content, fixed = fix_existing_links(content, current_num)
    content, linked = link_plain_text(content, current_num)
    total = fixed + linked

    if total and not dry_run:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    if total:
        print(
            f"{'[dry-run] ' if dry_run else ''}{filepath}: "
            f"{fixed} existing link(s) fixed, {linked} new link(s) created"
        )

    return total


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

    print(f"\nDone. {total} change(s) {'would be ' if args.dry_run else ''}made.")


if __name__ == "__main__":
    main()
