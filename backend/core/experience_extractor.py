import re
from datetime import datetime
from typing import Optional

MONTHS = "jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december"
DATE_RANGE = re.compile(rf"((?:{MONTHS})\.?\s+\d{{4}})\s*-\s*((?:{MONTHS})\.?\s+\d{{4}}|present|current)", re.IGNORECASE)
YEAR_SPAN = re.compile(r"(\d+(?:\.\d+)?)\s+years?\s+of\s+experience", re.IGNORECASE)
SINGLE_YEAR = re.compile(r"(\d{4})")

MONTH_NUM = {
    'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,'jul':7,'aug':8,'sep':9,'sept':9,'oct':10,'nov':11,'dec':12,
    'january':1,'february':2,'march':3,'april':4,'june':6,'july':7,'august':8,'september':9,'october':10,'november':11,'december':12
}


def parse_month_year(token: str) -> Optional[datetime]:
    token = token.lower().strip().replace('.', '')
    parts = token.split()
    if len(parts) != 2:
        return None
    m, y = parts
    if m not in MONTH_NUM:
        return None
    try:
        year = int(y)
    except ValueError:
        return None
    return datetime(year, MONTH_NUM[m], 1)


def compute_years(text: str) -> float:
    # explicit "X years of experience"
    span_match = YEAR_SPAN.search(text)
    if span_match:
        try:
            return float(span_match.group(1))
        except Exception:
            pass

    ranges = DATE_RANGE.findall(text)
    total_months = 0
    now = datetime.utcnow()
    for start_raw, end_raw in ranges:
        start_dt = parse_month_year(start_raw)
        end_dt = parse_month_year(end_raw) if end_raw.lower() not in ("present", "current") else now
        if start_dt and end_dt and end_dt >= start_dt:
            diff_months = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month)
            if diff_months > 0:
                total_months += diff_months
    if total_months:
        return round(total_months / 12.0, 2)

    # heuristic: use earliest and latest year numbers if date ranges missing
    years = [int(y) for y in SINGLE_YEAR.findall(text) if 1950 < int(y) < now.year + 1]
    if len(years) >= 2:
        span = max(years) - min(years)
        if span > 0:
            return float(span)
    return 0.0
