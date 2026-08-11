"""
ETL entrypoint for loading disaster records into PostgreSQL.

Usage:
    python -m etl.import_disasters                 # imports bundled seed data
    python -m etl.import_disasters --file path.json # imports a custom dataset
    python -m etl.import_disasters --usgs           # pulls the live USGS feed too

The import is idempotent: records are upserted by id, so re-running this
(e.g. from the scheduler) picks up edits to the seed file or newly appended
records without duplicating anything already in the database.
"""
import argparse
import json
import sys
from pathlib import Path

from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app import models
from etl.parse_casualties import parse_casualty_range

SEED_DIR = Path(__file__).parent
CATS_FILE = SEED_DIR / "cats_raw.json"
DISASTERS_FILE = SEED_DIR / "disasters_raw.json"

# Family grouping mirrors the frontend's chip groups.
FAMILY_BY_KEY = {
    "earthquake": "Geologic", "tsunami": "Geologic", "volcano": "Geologic",
    "landslide": "Geologic", "avalanche": "Geologic", "sinkhole": "Geologic",
    "tropicalCyclone": "Wind & Storms", "hurricane": "Wind & Storms", "typhoon": "Wind & Storms",
    "tornado": "Wind & Storms", "severeThunderstorm": "Wind & Storms", "blizzard": "Wind & Storms",
    "hailstorm": "Wind & Storms", "icestorm": "Wind & Storms", "duststorm": "Wind & Storms",
    "flood": "Water & Fire", "drought": "Water & Fire", "wildfire": "Water & Fire",
    "heatwave": "Temperature", "coldwave": "Temperature",
}


def upsert_categories(db: Session, cats: dict) -> int:
    count = 0
    for key, c in cats.items():
        existing = db.query(models.Category).filter(models.Category.key == key).first()
        if existing:
            existing.label = c["label"]
            existing.hex_color = c["hex"]
            existing.family = FAMILY_BY_KEY.get(key)
        else:
            db.add(models.Category(
                key=key, label=c["label"], hex_color=c["hex"],
                family=FAMILY_BY_KEY.get(key),
            ))
        count += 1
    db.commit()
    return count


_CASUALTY_LABEL_KEYWORDS = ("lives lost", "death", "died", "casualt", "fatalit")


def _casualty_stat_text(r: dict) -> str | None:
    """Pick whichever stat (1 or 2) is actually labeled as a death toll, if any."""
    for stat_key in ("stat1", "stat2"):
        stat = r.get(stat_key) or {}
        label = (stat.get("l") or "").lower()
        if any(kw in label for kw in _CASUALTY_LABEL_KEYWORDS):
            return stat.get("v")
    return None


def upsert_disasters(db: Session, records: list[dict], source: str = "curated") -> tuple[int, int]:
    created, updated = 0, 0
    for r in records:
        deaths_min, deaths_max = parse_casualty_range(_casualty_stat_text(r))

        fields = dict(
            name=r["name"],
            category_key=r["cat"],
            year=r["year"],
            event_date=r.get("date"),
            lat=r.get("lat"),
            lon=r.get("lon"),
            map_x=r.get("x"),
            map_y=r.get("y"),
            region=r.get("region"),
            stat1_label=(r.get("stat1") or {}).get("l"),
            stat1_value=(r.get("stat1") or {}).get("v"),
            stat2_label=(r.get("stat2") or {}).get("l"),
            stat2_value=(r.get("stat2") or {}).get("v"),
            est_deaths_min=deaths_min,
            est_deaths_max=deaths_max,
            overview=r.get("overview"),
            fun_fact=r.get("fact"),
            source=source,
        )

        existing = db.query(models.Disaster).filter(models.Disaster.id == r["id"]).first()
        if existing:
            for k, v in fields.items():
                setattr(existing, k, v)
            updated += 1
        else:
            db.add(models.Disaster(id=r["id"], **fields))
            created += 1

    db.commit()
    return created, updated


def run(seed_file: Path = DISASTERS_FILE, include_usgs: bool = False):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        cats = json.loads(CATS_FILE.read_text())
        n_cats = upsert_categories(db, cats)
        print(f"Categories upserted: {n_cats}")

        records = json.loads(seed_file.read_text())
        created, updated = upsert_disasters(db, records, source="curated")
        print(f"Disasters — created: {created}, updated: {updated}")

        if include_usgs:
            from etl.usgs_feed import fetch_usgs_earthquakes
            live_records = fetch_usgs_earthquakes()
            c2, u2 = upsert_disasters(db, live_records, source="usgs_live")
            print(f"USGS live earthquakes — created: {c2}, updated: {u2}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=DISASTERS_FILE, help="Path to a disasters JSON file")
    parser.add_argument("--usgs", action="store_true", help="Also pull the live USGS significant-earthquakes feed")
    args = parser.parse_args()

    if not args.file.exists():
        print(f"Seed file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    run(seed_file=args.file, include_usgs=args.usgs)
