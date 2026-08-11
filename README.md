# Epicenter — Global Disaster Atlas

> A full-stack disaster intelligence platform for exploring, searching, analyzing, and understanding historical disasters through an interactive interface, REST API, automated data pipelines, and AI-powered summaries.

## Overview

Epicenter is a full-stack disaster atlas that combines an interactive frontend with a FastAPI backend and PostgreSQL database.

The platform provides:

* Interactive disaster visualization
* Search and filtering
* Historical disaster data
* REST API endpoints
* JWT-based authentication
* Disaster CRUD operations
* Analytics endpoints
* ETL data ingestion
* Scheduled data updates
* Optional LLM-powered disaster summaries

The backend currently supports 117 curated disaster records across 20 categories.

## Architecture

```text
                         ┌──────────────────┐
                         │    Frontend      │
                         │ Interactive Map  │
                         └────────┬─────────┘
                                  │
                              REST API
                                  │
                         ┌────────▼─────────┐
                         │     FastAPI      │
                         │   API Layer      │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
              PostgreSQL      Analytics      Claude API
                    ▲                           │
                    │                           ▼
                    │                    AI Summaries
                    │
              ┌─────┴──────┐
              │     ETL    │
              │ Data Import│
              └─────┬──────┘
                    │
             Curated / USGS
                 Data
```

## Tech Stack

### Frontend

* HTML
* CSS
* JavaScript

### Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* PostgreSQL

### Authentication

* JWT
* bcrypt

### Data Engineering

* ETL pipeline
* APScheduler
* USGS earthquake feed integration

### AI

* Anthropic Claude API
* LLM-powered disaster summaries

### Infrastructure

* Docker
* Docker Compose

## Core Features

### Interactive Disaster Atlas

Users can explore historical disaster records through an interactive geographic interface.

### REST API

The backend exposes REST endpoints for:

* Authentication
* Disaster records
* Filtering
* Searching
* Analytics
* CRUD operations
* AI-powered summaries

### Authentication

The API supports:

```text
Register
   ↓
Login
   ↓
JWT Token
   ↓
Authenticated Requests
```

Public read operations are available without authentication, while write operations require authentication.

### Analytics

The API provides aggregate statistics including:

* Total disasters
* Disasters by category
* Disasters by decade
* Deadliest disasters

### ETL Pipeline

The ETL layer imports and transforms disaster data before storing it in PostgreSQL.

```text
Raw Data
   ↓
Parsing
   ↓
Transformation
   ↓
PostgreSQL
   ↓
FastAPI
   ↓
Frontend
```

The importer is designed to be idempotent so that repeated imports update existing records rather than duplicating them.

### AI-Powered Summaries

Epicenter includes an optional Claude-powered summarization endpoint.

```text
Disaster Record
      ↓
FastAPI
      ↓
Claude API
      ↓
Generated Summary
      ↓
PostgreSQL
      ↓
Frontend
```

## API

### Health

```http
GET /health
```

### Authentication

```http
POST /auth/register
POST /auth/login
GET /auth/me
```

### Categories

```http
GET /api/categories
```

### Disasters

```http
GET /api/disasters
GET /api/disasters/{id}
POST /api/disasters
PATCH /api/disasters/{id}
DELETE /api/disasters/{id}
```

Filtering and search parameters include:

```text
category
year_min
year_max
q
limit
offset
sort
```

### Analytics

```http
GET /api/analytics/summary
GET /api/analytics/by-category
GET /api/analytics/by-decade
GET /api/analytics/deadliest
```

### AI Summarization

```http
POST /api/disasters/{id}/summarize
```

## Running Locally

### Docker

```bash
cp .env.example .env
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

Interactive FastAPI documentation:

```text
http://localhost:8000/docs
```

### Without Docker

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure PostgreSQL and environment variables, then import the seed data:

```bash
python -m etl.import_disasters
```

Start the API:

```bash
uvicorn app.main:app --reload
```

## Documentation

Detailed technical documentation is available in:

* [Architecture](docs/architecture.md)
* [API Guide](docs/api-guide.md)
* [Authentication](docs/authentication.md)
* [ETL Pipeline](docs/etl-guide.md)
* [AI Integration](docs/ai-integration.md)

## Tutorials

Tutorials are being developed alongside the project:

* API Fundamentals
* REST API Integration
* Webhooks
* n8n Automation
* AI API Integration

## Testing

The backend has been tested against a PostgreSQL and FastAPI stack, including:

* ETL import
* Idempotent data re-import
* API filtering and search
* Authentication
* CRUD operations
* Protected write operations
* Analytics endpoints
* AI summarization error handling

## Project Goals

Epicenter is also being developed as a technical education project.

The goal is to demonstrate how a real application can be:

1. Designed
2. Built
3. Documented
4. Integrated with external APIs
5. Connected to automation platforms
6. Extended with AI
7. Explained to both technical and non-technical users

## Future Improvements

* Production database migrations with Alembic
* Tighter CORS configuration
* Additional external data sources
* Webhook-based event integrations
* n8n automation workflows
* AI-agent integrations
* Expanded technical tutorials

## Author

**P M**

Data Science undergraduate interested in AI, APIs, automation, and developer education.
