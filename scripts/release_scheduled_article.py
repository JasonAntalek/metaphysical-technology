#!/usr/bin/env python3
"""Publish one approved Metaphysical Technology article on its release date."""

from __future__ import annotations

import argparse
import re
import subprocess
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "1b9a4546bb95fd0ecc868a0fe5e7e2d4045f1490"
SITE = "https://jasonantalek.github.io/metaphysical-technology"

RELEASES = [
    {
        "order": 8,
        "date": date(2026, 8, 13),
        "file": "articles/08_Where_Metaphysical_Technology_Begins.md",
        "title": "Where Metaphysical Technology Begins",
        "permalink": "/articles/where-metaphysical-technology-begins/",
    },
    {
        "order": 9,
        "date": date(2026, 8, 14),
        "file": "articles/09_What_Happened_and_What_It_Means_Are_Different_Questions.md",
        "title": "What Happened and What It Means Are Different Questions",
        "permalink": "/articles/what-happened-and-what-it-means-are-different-questions/",
    },
    {
        "order": 10,
        "date": date(2026, 8, 16),
        "file": "articles/10_The_Experience_Belongs_to_the_Human_Not_the_System.md",
        "title": "The Experience Belongs to the Human, Not the System",
        "permalink": "/articles/the-experience-belongs-to-the-human-not-the-system/",
    },
    {
        "order": 11,
        "date": date(2026, 8, 18),
        "file": "articles/11_Building_Is_Not_Proof_It_Can_Still_Be_Research.md",
        "title": "Building Is Not Proof. It Can Still Be Research.",
        "permalink": "/articles/building-is-not-proof-it-can-still-be-research/",
    },
    {
        "order": 12,
        "date": date(2026, 8, 20),
        "file": "articles/12_The_AI_Didnt_Produce_the_Result_The_Relationship_Did.md",
        "title": "The AI Didn’t Produce the Result. The Relationship Did.",
        "permalink": "/articles/the-ai-didnt-produce-the-result-the-relationship-did/",
    },
    {
        "order": 13,
        "date": date(2026, 8, 22),
        "file": "articles/13_A_Project_That_Remembers_Can_Learn.md",
        "title": "A Project That Remembers Can Learn",
        "permalink": "/articles/a-project-that-remembers-can-learn/",
    },
    {
        "order": 14,
        "date": date(2026, 8, 24),
        "file": "articles/14_If_Failure_Is_Missing_Research_Is_Missing.md",
        "title": "If Failure Is Missing, Research Is Missing",
        "permalink": "/articles/if-failure-is-missing-research-is-missing/",
    },
    {
        "order": 15,
        "date": date(2026, 8, 26),
        "file": "articles/15_A_Category_Cannot_Validate_Itself.md",
        "title": "A Category Cannot Validate Itself",
        "permalink": "/articles/a-category-cannot-validate-itself/",
    },
]


def run(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def replace_front_matter_fields(text: str, updates: dict[str, str | None]) -> str:
    if not text.startswith("---\n"):
        raise ValueError("Article is missing YAML front matter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("Article has unclosed YAML front matter")

    lines = text[4:end].splitlines()
    keys = set(updates)
    lines = [line for line in lines if line.split(":", 1)[0] not in keys]
    for key, value in updates.items():
        if value is not None:
            lines.append(f"{key}: {value}")
    return "---\n" + "\n".join(lines) + text[end:]


def select_release(requested: str, today: date) -> dict | None:
    if requested != "auto":
        order = int(requested)
        release = next((item for item in RELEASES if item["order"] == order), None)
        if release is None or order < 9:
            raise ValueError("Manual release order must be between 9 and 15")
        return release

    for release in RELEASES[1:]:
        if release["date"] <= today and not (ROOT / release["file"]).exists():
            return release
    return None


def update_previous_article(release: dict) -> None:
    previous = next(item for item in RELEASES if item["order"] == release["order"] - 1)
    path = ROOT / previous["file"]
    if not path.exists():
        raise RuntimeError(f"Previous article is not published: {path}")
    text = path.read_text(encoding="utf-8")
    text = replace_front_matter_fields(
        text,
        {"next_url": release["permalink"], "next_title": release["title"]},
    )
    path.write_text(text, encoding="utf-8")


def update_article_index(release: dict) -> None:
    path = ROOT / "articles/index.md"
    text = path.read_text(encoding="utf-8")
    if release["permalink"] in text:
        return
    marker = "</ol>"
    position = text.rfind(marker)
    if position == -1:
        raise RuntimeError("Article index list was not found")
    item = (
        f"  <li><a href=\"{{{{ '{release['permalink']}' | relative_url }}}}\">"
        f"<span>Article {release['order']}</span>{release['title']}</a></li>\n"
    )
    path.write_text(text[:position] + item + text[position:], encoding="utf-8")


def update_llms_navigation(release: dict) -> None:
    path = ROOT / "llms.txt"
    text = path.read_text(encoding="utf-8")
    if release["permalink"] in text:
        return
    marker = "\n## Machine-readable records"
    if marker not in text:
        raise RuntimeError("llms.txt article insertion point was not found")
    item = (
        f"- [{release['order']}. {release['title']}]"
        f"({{{{ '{release['permalink']}' | absolute_url }}}})\n"
    )
    path.write_text(text.replace(marker, "\n" + item + marker, 1), encoding="utf-8")


def update_sitemap(release: dict, published_on: date) -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    url = SITE + release["permalink"]
    if url in text:
        return
    marker = "\n</urlset>"
    if marker not in text:
        raise RuntimeError("Sitemap insertion point was not found")
    block = (
        "\n  <url>\n"
        f"    <loc>{url}</loc>\n"
        f"    <lastmod>{published_on.isoformat()}</lastmod>\n"
        "    <priority>0.8</priority>\n"
        "  </url>"
    )
    path.write_text(text.replace(marker, block + marker, 1), encoding="utf-8")


def update_corpus_builder(release: dict, published_on: date) -> None:
    path = ROOT / "scripts/build_llms_full.py"
    text = path.read_text(encoding="utf-8")
    record = f'    ("ARTICLE {release["order"]}", ROOT / "{release["file"]}"),'
    if record not in text:
        marker = "]\n\n\ndef strip_front_matter"
        if marker not in text:
            raise RuntimeError("Corpus record insertion point was not found")
        text = text.replace(marker, record + "\n" + marker, 1)
    version = f"1.{release['order'] - 7}.0"
    text = re.sub(r'"Version: [^"]+"', f'"Version: {version}"', text, count=1)
    text = re.sub(
        r'"Released: [0-9]{4}-[0-9]{2}-[0-9]{2}"',
        f'"Released: {published_on.isoformat()}"',
        text,
        count=1,
    )
    path.write_text(text, encoding="utf-8")
    subprocess.check_call(["python3", str(path)], cwd=ROOT)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--article-order", default="auto")
    args = parser.parse_args()

    today = datetime.now(ZoneInfo("America/Denver")).date()
    release = select_release(args.article_order, today)
    if release is None:
        print("No article is due for release.")
        return 0

    target = ROOT / release["file"]
    if target.exists():
        print(f"Article {release['order']} is already published.")
        return 0

    source = run("git", "show", f"{SOURCE_COMMIT}:{release['file']}") + "\n"
    source = replace_front_matter_fields(source, {"next_url": None, "next_title": None})
    target.write_text(source, encoding="utf-8")

    update_previous_article(release)
    update_article_index(release)
    update_llms_navigation(release)
    update_sitemap(release, today)
    update_corpus_builder(release, today)

    print(f"Prepared Article {release['order']}: {release['title']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
