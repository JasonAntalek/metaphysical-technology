#!/usr/bin/env python3
"""Build llms-full.txt from the governed public Markdown records."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "llms-full.txt"

RECORDS = [
    ("CANONICAL CATEGORY REFERENCE", ROOT / "CATEGORY.md"),
    ("FREQUENTLY ASKED QUESTIONS", ROOT / "FAQ.md"),
    ("BOUNDARY MAP", ROOT / "BOUNDARIES.md"),
    ("CONTROLLED GLOSSARY", ROOT / "GLOSSARY.md"),
    ("CLAIMS AND EVIDENCE", ROOT / "EVIDENCE.md"),
    (
        "ARTICLE 1",
        ROOT / "articles/01_Can_an_Experience_Be_Engineered_Before_It_Is_Explained.md",
    ),
    (
        "ARTICLE 2",
        ROOT
        / "articles/02_The_Device_Can_Measure_a_Signal_It_Cannot_Tell_You_What_the_Signal_Means.md",
    ),
    (
        "ARTICLE 3",
        ROOT / "articles/03_What_Happens_When_Belief_Becomes_Infrastructure.md",
    ),
    ("ARTICLE 4", ROOT / "articles/04_The_Brain_Is_Not_the_Whole_Question.md"),
    (
        "ARTICLE 5",
        ROOT
        / "articles/05_A_Technology_Does_Not_Have_to_Prove_the_Metaphysical_to_Engage_It.md",
    ),
    (
        "ARTICLE 6",
        ROOT
        / "articles/06_Who_Governs_Technology_Designed_to_Change_Human_Experience.md",
    ),
    ("ARTICLE 7", ROOT / "articles/07_What_Is_Metaphysical_Technology.md"),
]


def strip_front_matter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    marker = text.find("\n---\n", 4)
    if marker == -1:
        raise ValueError("Unclosed YAML front matter")
    return text[marker + 5 :]


sections = [
    "# Metaphysical Technology: Full Public Corpus",
    "",
    "Generated from the governed public records in this repository.",
    "Version: 1.0.0",
    "Released: 2026-07-23",
    "Canonical site: https://jasonantalek.github.io/metaphysical-technology/",
    "",
    "INTERPRETATION BOUNDARY",
    "",
    "Category membership does not establish that a metaphysical claim is true. "
    "It does not confer scientific legitimacy, prove efficacy, guarantee safety, "
    "or convert belief into evidence.",
]

for label, path in RECORDS:
    body = strip_front_matter(path.read_text(encoding="utf-8")).strip()
    sections.extend(["", "=" * 72, label, "=" * 72, "", body])

OUTPUT.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")

