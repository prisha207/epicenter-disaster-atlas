from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, disasters, analytics, llm
from etl.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables if they don't exist yet. For a real production system,
    # swap this for Alembic migrations.
    Base.metadata.create_all(bind=engine)
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Epicenter API",
    description="Backend for the Epicenter disaster atlas — disasters stored in "
                "PostgreSQL, served over REST, with JWT auth, analytics, and "
                "scheduled ETL updates.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your frontend's origin in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(disasters.router)
app.include_router(analytics.router)
app.include_router(llm.router)


@app.get("/health")
def health():
    return {"status": "ok"}
