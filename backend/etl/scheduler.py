"""
Runs the ETL import on a schedule using APScheduler, inside the FastAPI
process. Started/stopped from app.main's lifespan handler.

For a heavier production setup you'd likely run this as a separate worker
process (e.g. via `python -m etl.scheduler` + cron, or Celery beat) instead
of in-process — see the __main__ block below for a standalone entrypoint.
"""
import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.config import settings
from etl.import_disasters import run as run_etl

logger = logging.getLogger("epicenter.scheduler")
_scheduler: BackgroundScheduler | None = None


def _job():
    logger.info("Scheduled ETL run starting...")
    try:
        run_etl(include_usgs=True)
    except Exception:
        logger.exception("Scheduled ETL run failed")
    else:
        logger.info("Scheduled ETL run complete.")


def start_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    _scheduler = BackgroundScheduler(timezone="UTC")
    _scheduler.add_job(
        _job,
        trigger="interval",
        hours=settings.etl_schedule_hours,
        id="etl_refresh",
        next_run_time=None,  # don't fire immediately on boot; seed data is loaded at startup already
    )
    _scheduler.start()
    logger.info(f"Scheduler started — ETL will re-run every {settings.etl_schedule_hours}h")
    return _scheduler


def stop_scheduler():
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None


if __name__ == "__main__":
    # Standalone worker: `python -m etl.scheduler` runs the job loop without
    # starting the API server — useful if you want ETL on its own process/pod.
    logging.basicConfig(level=logging.INFO)
    scheduler = start_scheduler()
    scheduler.get_job("etl_refresh").modify(next_run_time=None)
    run_etl(include_usgs=True)  # run once immediately, then let the schedule take over
    try:
        import time
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        stop_scheduler()
