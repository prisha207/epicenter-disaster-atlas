# AI Integration Guide

Epicenter includes an optional Claude-powered summarization feature.

## Architecture

```text
Frontend
   ↓
FastAPI
   ↓
LLM Service
   ↓
Claude API
   ↓
Generated Summary
   ↓
PostgreSQL
   ↓
Frontend
```

## Endpoint

```http
POST /api/disasters/{id}/summarize
```

The endpoint retrieves the structured disaster record and sends relevant information to Claude.

Claude generates a short summary.

The generated summary is stored with the disaster record.

## Why Use an LLM?

The database contains structured information.

For example:

```text
Name
Date
Location
Category
Death Toll
Magnitude
```

An LLM can transform these structured fields into a concise human-readable explanation.

## Example Workflow

```text
Structured Data
      ↓
API Request
      ↓
LLM
      ↓
Natural Language
      ↓
User
```

## Configuration

The feature requires:

```text
ANTHROPIC_API_KEY
```

The model can optionally be configured through:

```text
ANTHROPIC_MODEL
```

Without an API key, the summarization endpoint returns an appropriate configuration error instead of attempting the external API call.

## Integration Pattern

The important architectural pattern is:

```text
Application
    ↓
Backend API
    ↓
External AI API
    ↓
Structured Response
    ↓
Application
```

This same pattern can be used to integrate many external AI services into a SaaS application.
