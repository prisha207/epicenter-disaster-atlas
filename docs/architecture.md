
# Epicenter Architecture

## System Overview

Epicenter is organized into four major layers:

```text
Frontend
   ↓
FastAPI REST API
   ↓
PostgreSQL
   ↑
ETL Pipeline
```

An optional AI layer connects the API to Claude.

```text
Frontend
   ↓
FastAPI
   ↓
Claude API
   ↓
Generated Summary
```

## Components

### Frontend

The frontend provides the interactive disaster visualization and user interface.

It communicates with the backend through HTTP requests.

### FastAPI

FastAPI acts as the application's API layer.

It handles:

* HTTP requests
* Authentication
* Validation
* CRUD operations
* Filtering
* Analytics
* AI summarization

### PostgreSQL

PostgreSQL stores:

* Users
* Categories
* Disaster records
* Generated summaries

### SQLAlchemy

SQLAlchemy provides the database abstraction layer between Python and PostgreSQL.

### ETL

The ETL system imports disaster data into the database.

```text
Source Data
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
```

### Scheduler

APScheduler can periodically execute the ETL process.

### Claude

The optional Claude integration generates short summaries from structured disaster information.

## Request Flow

A typical frontend request follows this flow:

```text
User
 ↓
Frontend
 ↓
HTTP GET
 ↓
FastAPI Router
 ↓
Database Query
 ↓
PostgreSQL
 ↓
JSON Response
 ↓
Frontend
 ↓
UI Update
```

## Authentication Flow

```text
User
 ↓
POST /auth/register
 ↓
POST /auth/login
 ↓
JWT
 ↓
Authorization Header
 ↓
Protected API Endpoint
```

## Design Principles

The project separates:

* API routing
* Database models
* Validation schemas
* Authentication
* Business logic
* ETL
* AI services

This makes the system easier to maintain and document.
