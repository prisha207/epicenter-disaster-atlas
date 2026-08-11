"""
Pulls the USGS "significant earthquakes, past month" GeoJSON feed and maps
each feature into the same record shape used by the curated seed data, so it
can flow through the same upsert_disasters() function.

Note: this requires outbound internet access to earthquake.usgs.gov, which
may not be reachable from every sandboxed environment. It's wired into the
scheduler (etl/scheduler.py) and into `import_disasters.py --usgs`, but is
safe to leave disabled if that endpoint isn't reachable — the rest of the
ETL/API will keep working off the curated dataset either way.
"""
import datetime as dt

import httpx

from app.config import settings


def _map_x(lon: float) -> float:
    return (lon + 180) / 360 * 1000


def _map_y(lat: float) -> float:
    return (90 - lat) / 180 * 500


def fetch_usgs_earthquakes(timeout: float = 15.0) -> list[dict]:
    """Returns a list of records shaped like the curated seed JSON."""
    try:
        resp = httpx.get(settings.usgs_feed_url, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:  # network errors, bad JSON, etc.
        print(f"[usgs_feed] fetch failed, skipping live import: {exc}")
        return []

    records = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        geom = feature.get("geometry", {})
        coords = geom.get("coordinates", [None, None, None])
        lon, lat = coords[0], coords[1]
        if lon is None or lat is None:
            continue

        event_id = f"usgs_{feature.get('id')}"
        time_ms = props.get("time")
        event_dt = dt.datetime.utcfromtimestamp(time_ms / 1000) if time_ms else None
        mag = props.get("mag")

        records.append({
            "id": event_id,
            "name": props.get("title") or props.get("place") or "Earthquake",
            "cat": "earthquake",
            "year": event_dt.year if event_dt else dt.datetime.utcnow().year,
            "date": event_dt.strftime("%B %-d, %Y") if event_dt else None,
            "lat": lat,
            "lon": lon,
            "x": _map_x(lon),
            "y": _map_y(lat),
            "region": props.get("place"),
            "stat1": {"l": "Magnitude", "v": f"{mag} Mw" if mag is not None else "Unknown"},
            "stat2": {"l": "Source", "v": "USGS live feed"},
            "overview": f"Automatically imported from the USGS significant earthquakes feed. "
                        f"{props.get('place') or ''}".strip(),
            "fact": None,
        })
    return records
