import re
from typing import List

HEADER_FOOTER_PAT = re.compile(r"(^Page \d+ of \d+)|(^\s*Page \d+\s*$)", re.IGNORECASE | re.MULTILINE)
PAGE_NUMBER_PAT = re.compile(r"\n?\s*\d+\s*\n")
MULTISPACE = re.compile(r"[ \t]{2,}")
SYMBOLS = re.compile(r"[•■▪▶★✦–—]+")


def remove_headers_footers(text: str) -> str:
    return HEADER_FOOTER_PAT.sub(" ", text)


def remove_page_numbers(text: str) -> str:
    return PAGE_NUMBER_PAT.sub(" \n", text)


def remove_symbols(text: str) -> str:
    return SYMBOLS.sub(" ", text)


def normalize_whitespace(text: str) -> str:
    text = MULTISPACE.sub(" ", text)
    text = re.sub(r"\r", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_text(raw: str) -> str:
    t = remove_headers_footers(raw)
    t = remove_page_numbers(t)
    t = remove_symbols(t)
    t = normalize_whitespace(t)
    return t
