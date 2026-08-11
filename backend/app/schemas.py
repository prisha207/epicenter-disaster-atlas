import datetime as dt

from pydantic import BaseModel, EmailStr, ConfigDict, Field


# ---------- Categories ----------
class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    key: str
    label: str
    hex_color: str
    family: str | None = None


# ---------- Disasters ----------
class DisasterBase(BaseModel):
    name: str
    category_key: str
    year: int
    event_date: str | None = None
    lat: float | None = None
    lon: float | None = None
    map_x: float | None = None
    map_y: float | None = None
    region: str | None = None
    stat1_label: str | None = None
    stat1_value: str | None = None
    stat2_label: str | None = None
    stat2_value: str | None = None
    est_deaths_min: int | None = None
    est_deaths_max: int | None = None
    overview: str | None = None
    fun_fact: str | None = None
    source: str = "manual"


class DisasterCreate(DisasterBase):
    id: str = Field(..., description="Unique slug id, e.g. 'tohoku2011'")


class DisasterUpdate(BaseModel):
    """All fields optional — PATCH-style partial update."""
    name: str | None = None
    category_key: str | None = None
    year: int | None = None
    event_date: str | None = None
    lat: float | None = None
    lon: float | None = None
    map_x: float | None = None
    map_y: float | None = None
    region: str | None = None
    stat1_label: str | None = None
    stat1_value: str | None = None
    stat2_label: str | None = None
    stat2_value: str | None = None
    est_deaths_min: int | None = None
    est_deaths_max: int | None = None
    overview: str | None = None
    fun_fact: str | None = None
    llm_summary: str | None = None


class DisasterOut(DisasterBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    llm_summary: str | None = None
    created_at: dt.datetime
    updated_at: dt.datetime
    category: CategoryOut | None = None


class DisasterListResponse(BaseModel):
    total: int
    items: list[DisasterOut]


# ---------- Auth ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    is_admin: bool
    created_at: dt.datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Analytics ----------
class CategoryCount(BaseModel):
    category_key: str
    label: str
    count: int


class DecadeCount(BaseModel):
    decade: int
    count: int


class AnalyticsSummary(BaseModel):
    total_disasters: int
    total_categories: int
    earliest_year: int | None
    latest_year: int | None
    by_category: list[CategoryCount]
    by_decade: list[DecadeCount]
    deadliest: list[DisasterOut]
