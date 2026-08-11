from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/by-category", response_model=list[schemas.CategoryCount])
def by_category(db: Session = Depends(get_db)):
    rows = (
        db.query(models.Disaster.category_key, models.Category.label, func.count(models.Disaster.id))
        .join(models.Category, models.Category.key == models.Disaster.category_key)
        .group_by(models.Disaster.category_key, models.Category.label)
        .order_by(func.count(models.Disaster.id).desc())
        .all()
    )
    return [schemas.CategoryCount(category_key=k, label=lbl, count=c) for k, lbl, c in rows]


@router.get("/by-decade", response_model=list[schemas.DecadeCount])
def by_decade(db: Session = Depends(get_db)):
    # NOTE: (year / 10) * 10 looks like integer-bucketing but SQLAlchemy/psycopg2
    # can promote the literal `10` to NUMERIC, turning this into true division
    # that cancels itself out and returns the original year. Subtraction +
    # modulo stays in integer arithmetic the whole way through.
    decade_expr = models.Disaster.year - (models.Disaster.year % 10)
    rows = (
        db.query(decade_expr.label("decade"), func.count(models.Disaster.id))
        .group_by("decade")
        .order_by("decade")
        .all()
    )
    return [schemas.DecadeCount(decade=int(d), count=c) for d, c in rows]


@router.get("/deadliest", response_model=list[schemas.DisasterOut])
def deadliest(db: Session = Depends(get_db), limit: int = Query(10, ge=1, le=100)):
    return (
        db.query(models.Disaster)
        .filter(models.Disaster.est_deaths_max.isnot(None))
        .order_by(models.Disaster.est_deaths_max.desc())
        .limit(limit)
        .all()
    )


@router.get("/summary", response_model=schemas.AnalyticsSummary)
def summary(db: Session = Depends(get_db)):
    total = db.query(models.Disaster).count()
    total_categories = db.query(models.Category).count()
    min_year = db.query(func.min(models.Disaster.year)).scalar()
    max_year = db.query(func.max(models.Disaster.year)).scalar()

    cat_rows = by_category(db)  # reuse
    decade_rows = by_decade(db)
    top_deadly = deadliest(db, limit=10)

    return schemas.AnalyticsSummary(
        total_disasters=total,
        total_categories=total_categories,
        earliest_year=min_year,
        latest_year=max_year,
        by_category=cat_rows,
        by_decade=decade_rows,
        deadliest=top_deadly,
    )
