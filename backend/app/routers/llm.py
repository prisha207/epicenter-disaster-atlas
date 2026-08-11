from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.dependencies import get_current_user
from app.services.llm_summary import summarize_disaster, LLMNotConfigured

router = APIRouter(prefix="/api", tags=["llm"])


@router.post("/disasters/{disaster_id}/summarize")
def summarize(
    disaster_id: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    obj = db.query(models.Disaster).filter(models.Disaster.id == disaster_id).first()
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Disaster not found")

    try:
        summary = summarize_disaster(obj)
    except LLMNotConfigured:
        raise HTTPException(
            status.HTTP_501_NOT_IMPLEMENTED,
            detail="Set ANTHROPIC_API_KEY on the server to enable LLM summarization",
        )

    obj.llm_summary = summary
    db.commit()
    db.refresh(obj)
    return {"id": obj.id, "llm_summary": obj.llm_summary}
