import re
from typing import Dict, List, Tuple

SECTION_KEYWORDS = {
    "skills": ["skills", "technical skills", "core competencies"],
    "experience": ["experience", "work history", "employment", "professional experience"],
    "projects": ["projects", "project work"],
    "education": ["education", "academic"],
    "summary": ["summary", "professional summary", "profile", "overview"],
    "certifications": ["certifications", "certification", "licenses"],
    "contact": ["contact", "contact information", "personal details"],
}

HEADER_PATTERN = re.compile(r"^\s*(.+?)\s*$")


def classify_sections(text: str) -> Dict[str, str]:
    lines = text.splitlines()
    current_header = None
    buckets: Dict[str, List[str]] = {k: [] for k in SECTION_KEYWORDS.keys()}

    def match_section(header: str) -> str:
        hl = header.lower()
        for sec, keys in SECTION_KEYWORDS.items():
            for k in keys:
                if hl.startswith(k):
                    return sec
        return ""

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        # treat lines in ALLCAPS or short lines as potential headers
        if (len(line_clean) < 60 and (line_clean.isupper() or line_clean.lower() in sum(SECTION_KEYWORDS.values(), []))):
            sec = match_section(line_clean)
            if sec:
                current_header = sec
                continue
        if current_header:
            buckets[current_header].append(line)

    return {k: "\n".join(v).strip() for k, v in buckets.items() if v}
