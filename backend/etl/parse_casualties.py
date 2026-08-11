"""
Best-effort extraction of numeric casualty ranges from free-text stat strings
like "~230,000", "55,000-60,000+", "100,000-160,000+", "1-4 million", or
"Direct lives lost: ~6". Returns (min, max) as ints, or (None, None) if no
usable number is found (e.g. "Low (remote region)").

This is deliberately conservative: it's used for sorting/ranking in the
analytics dashboards, not as an authoritative casualty figure.
"""
import re

_NUMBER_RE = re.compile(r"([\d,]+(?:\.\d+)?)\s*(million|k)?", re.IGNORECASE)


def _to_int(num_str: str, suffix: str | None) -> int:
    value = float(num_str.replace(",", ""))
    if suffix and suffix.lower() == "million":
        value *= 1_000_000
    elif suffix and suffix.lower() == "k":
        value *= 1_000
    return int(value)


def parse_casualty_range(text: str | None) -> tuple[int | None, int | None]:
    if not text:
        return None, None

    matches = [
        (m.group(1), m.group(2))
        for m in _NUMBER_RE.finditer(text)
        if m.group(1).replace(",", "").replace(".", "").isdigit()
    ]
    if not matches:
        return None, None

    # A shared suffix like "million" often trails only the last number in a
    # range ("1-4 million"). If exactly one match carries a suffix, apply it
    # to every match in the range.
    suffixes = {suf.lower() for _, suf in matches if suf}
    if len(suffixes) == 1:
        shared_suffix = next(iter(suffixes))
        matches = [(num, suf or shared_suffix) for num, suf in matches]

    values = sorted(_to_int(num, suf) for num, suf in matches)

    if len(values) == 1:
        return values[0], values[0]
    return values[0], values[-1]


if __name__ == "__main__":
    samples = [
        "~230,000",
        "55,000-60,000+",
        "100,000-160,000+",
        "1-4 million",
        "Direct lives lost: ~6",
        "Low (remote region)",
        "246",
        "700+ (incl. indirect)",
    ]
    for s in samples:
        print(f"{s!r:35} -> {parse_casualty_range(s)}")
