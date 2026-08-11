import datetime as dt

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    key = Column(String(40), primary_key=True)          # e.g. "earthquake"
    label = Column(String(80), nullable=False)           # e.g. "Earthquake"
    hex_color = Column(String(9), nullable=False)         # e.g. "#E8735A"
    family = Column(String(40), nullable=True)            # e.g. "Geologic"

    disasters = relationship("Disaster", back_populates="category")


class Disaster(Base):
    __tablename__ = "disasters"

    id = Column(String(60), primary_key=True)             # slug id, e.g. "tohoku2011"
    name = Column(String(200), nullable=False)
    category_key = Column(String(40), ForeignKey("categories.key"), nullable=False, index=True)

    year = Column(Integer, nullable=False, index=True)
    event_date = Column(String(80), nullable=True)         # human-readable date/date range

    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    map_x = Column(Float, nullable=True)                   # precomputed 0-1000 stylized map coords
    map_y = Column(Float, nullable=True)                   # precomputed 0-500 stylized map coords
    region = Column(String(200), nullable=True)

    stat1_label = Column(String(60), nullable=True)
    stat1_value = Column(String(120), nullable=True)
    stat2_label = Column(String(60), nullable=True)
    stat2_value = Column(String(120), nullable=True)

    # Parsed-out numeric estimate of deaths, when derivable from stat text.
    # Nullable because not every category (e.g. sinkholes, drought) reports a clean death count.
    est_deaths_min = Column(Integer, nullable=True)
    est_deaths_max = Column(Integer, nullable=True)

    overview = Column(Text, nullable=True)
    fun_fact = Column(Text, nullable=True)

    source = Column(String(60), nullable=False, default="curated")  # curated | usgs_live | manual
    llm_summary = Column(Text, nullable=True)               # optional Claude-generated summary

    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    category = relationship("Category", back_populates="disasters")


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_user_email"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
