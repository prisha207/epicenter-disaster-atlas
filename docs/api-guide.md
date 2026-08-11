# Epicenter REST API Guide

## Base URL

When running locally:

```text
http://localhost:8000
```

FastAPI automatically provides interactive API documentation at:

```text
http://localhost:8000/docs
```

## Health Check

```http
GET /health
```

Example:

```bash
curl http://localhost:8000/health
```

## Get Disaster Records

```http
GET /api/disasters
```

The endpoint supports filtering and search.

Example:

```http
GET /api/disasters?category=Earthquake
```

Example with a year range:

```http
GET /api/disasters?year_min=2000&year_max=2020
```

Example search:

```http
GET /api/disasters?q=Japan
```

## Get a Single Disaster

```http
GET /api/disasters/{id}
```

Example:

```http
GET /api/disasters/1
```

## Categories

```http
GET /api/categories
```

## Analytics

Summary:

```http
GET /api/analytics/summary
```

By category:

```http
GET /api/analytics/by-category
```

By decade:

```http
GET /api/analytics/by-decade
```

Deadliest disasters:

```http
GET /api/analytics/deadliest?limit=10
```

## Authentication

Register:

```http
POST /auth/register
```

Login:

```http
POST /auth/login
```

The login endpoint returns a JWT.

Authenticated requests use:

```http
Authorization: Bearer YOUR_TOKEN
```

## CRUD

Authenticated users can create:

```http
POST /api/disasters
```

Update:

```http
PATCH /api/disasters/{id}
```

Delete:

```http
DELETE /api/disasters/{id}
```

## AI Summarization

```http
POST /api/disasters/{id}/summarize
```

The endpoint sends structured disaster information to Claude and stores the resulting summary.

## Example Integration

A client application can request:

```text
GET /api/disasters?category=Earthquake
```

The API returns JSON.

The client can then:

1. Parse the response
2. Extract disaster records
3. Display them
4. Apply additional client-side logic
5. Trigger another workflow

This request → response pattern is the foundation for integrating Epicenter with other applications and automation tools.
