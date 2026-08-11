"""
Optional LLM-powered summarization.

If ANTHROPIC_API_KEY is set, this calls Claude to generate a short, fresh
summary of a disaster record from its structured fields — useful for:
  - backfilling `overview`/`fun_fact` text for records imported from raw
    data feeds (e.g. USGS) that only have coordinates and numbers,
  - refreshing summaries in a different tone/length on demand.

If no API key is configured, `summarize_disaster` raises LLMNotConfigured
so the calling endpoint can return a clear 501 instead of failing oddly.
"""
from app.config import settings
from app import models


class LLMNotConfigured(RuntimeError):
    pass


def _client():
    if not settings.anthropic_api_key:
        raise LLMNotConfigured("ANTHROPIC_API_KEY is not set")
    import anthropic
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def summarize_disaster(disaster: models.Disaster) -> str:
    client = _client()

    facts = (
        f"Name: {disaster.name}\n"
        f"Category: {disaster.category_key}\n"
        f"Year: {disaster.year} ({disaster.event_date or 'date unknown'})\n"
        f"Region: {disaster.region or 'unknown'}\n"
        f"Key stat 1: {disaster.stat1_label}: {disaster.stat1_value}\n"
        f"Key stat 2: {disaster.stat2_label}: {disaster.stat2_value}\n"
        f"Existing overview: {disaster.overview or '(none)'}\n"
    )

    prompt = (
        "You are writing a short, factual, neutral 2-3 sentence summary of a "
        "historical natural disaster for a reference app. Use only the facts "
        "given below — do not invent casualty figures or dates that aren't "
        "provided. Do not use markdown, just plain prose.\n\n" + facts
    )

    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )

    parts = [block.text for block in response.content if getattr(block, "type", None) == "text"]
    return "".join(parts).strip()
