from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/api", tags=["disasters"])


@router.get("/categories", response_model=list[schemas.CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).order_by(models.Category.family, models.Category.label).all()


@router.get("/disasters", response_model=schemas.DisasterListResponse)
def list_disasters(
    db: Session = Depends(get_db),
    category: list[str] | None = Query(None, description="Repeat for multiple, e.g. ?category=earthquake&category=flood"),
    year_min: int | None = Query(None),
    year_max: int | None = Query(None),
    q: str | None = Query(None, description="Free-text search across name/region/overview"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    sort: str = Query("year", pattern="^(year|-year|name|-name)$"),
):
    query = db.query(models.Disaster)

    if category:
        query = query.filter(models.Disaster.category_key.in_(category))
    if year_min is not None:
        query = query.filter(models.Disaster.year >= year_min)
    if year_max is not None:
        query = query.filter(models.Disaster.year <= year_max)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                models.Disaster.name.ilike(like),
                models.Disaster.region.ilike(like),
                models.Disaster.overview.ilike(like),
            )
        )

    total = query.count()

    col = models.Disaster.year if sort.lstrip("-") == "year" else models.Disaster.name
    query = query.order_by(col.desc() if sort.startswith("-") else col.asc())

    items = query.offset(offset).limit(limit).all()
    return schemas.DisasterListResponse(total=total, items=items)


@router.get("/disasters/{disaster_id}", response_model=schemas.DisasterOut)
def get_disaster(disaster_id: str, db: Session = Depends(get_db)):
    obj = db.query(models.Disaster).filter(models.Disaster.id == disaster_id).first()
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Disaster not found")
    return obj


@router.post("/disasters", response_model=schemas.DisasterOut, status_code=status.HTTP_201_CREATED)
def create_disaster(
    payload: schemas.DisasterCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if db.query(models.Disaster).filter(models.Disaster.id == payload.id).first():
        raise HTTPException(status.HTTP_409_CONFLICT, detail="A disaster with this id already exists")
    if not db.query(models.Category).filter(models.Category.key == payload.category_key).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Unknown category_key")

    obj = models.Disaster(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/disasters/{disaster_id}", response_model=schemas.DisasterOut)
def update_disaster(
    disaster_id: str,
    payload: schemas.DisasterUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    obj = db.query(models.Disaster).filter(models.Disaster.id == disaster_id).first()
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Disaster not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)

    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/disasters/{disaster_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_disaster(
    disaster_id: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    obj = db.query(models.Disaster).filter(models.Disaster.id == disaster_id).first()
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Disaster not found")
    db.delete(obj)
    db.commit()
