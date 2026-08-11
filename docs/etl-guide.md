# ETL Pipeline Guide

Epicenter uses an ETL pipeline to move disaster data into PostgreSQL.

## ETL

ETL stands for:

```text
Extract
Transform
Load
```

## Epicenter Pipeline

```text
Raw Disaster Data
        ↓
     Extract
        ↓
      Parse
        ↓
    Transform
        ↓
      Validate
        ↓
       Upsert
        ↓
   PostgreSQL
        ↓
    FastAPI
        ↓
    Frontend
```

## Extract

The importer reads disaster data from the available source files.

An optional USGS earthquake feed can also be used.

## Transform

The pipeline converts source information into the application's database structure.

Casualty information is also parsed from free-text fields into numeric ranges when possible.

## Load

The transformed records are inserted or updated in PostgreSQL.

The importer is idempotent.

This means running the importer repeatedly does not create duplicate records for the same IDs.

## Scheduled Updates

APScheduler can periodically execute the ETL process.

The default schedule is configurable through:

```text
ETL_SCHEDULE_HOURS
```

## Running the ETL

Seed the curated data:

```bash
python -m etl.import_disasters
```

Include the optional USGS feed:

```bash
python -m etl.import_disasters --usgs
```

Use another JSON file:

```bash
python -m etl.import_disasters --file other.json
```

## Why ETL Matters

The ETL layer keeps data ingestion separate from the API layer.

This means the API can focus on serving clean structured data while the ETL system handles ingestion and transformation.
