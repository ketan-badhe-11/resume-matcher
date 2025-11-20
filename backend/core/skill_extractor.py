import json
import os
import re
from typing import List

SKILL_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "skill_dict.json")
WORD_PATTERN = re.compile(r"[A-Za-z][A-Za-z+.#]*")

try:
    with open(SKILL_JSON_PATH, "r", encoding="utf-8") as f:
        SKILL_DICT = set(json.load(f))
except Exception:
    SKILL_DICT = set(["python", "aws", "react", "sql", "docker", "kubernetes"])


def extract_skills(text: str) -> List[str]:
    words = set(w.lower() for w in WORD_PATTERN.findall(text))
    found = [skill for skill in SKILL_DICT if skill.lower() in words]
    # Capitalize nicely
    cleaned = sorted(set(s.capitalize() for s in found))
    return cleaned
