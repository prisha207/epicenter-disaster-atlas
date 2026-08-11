# Authentication Guide

Epicenter uses JWT-based authentication for protected operations.

## Authentication Flow

```text
Client
  ↓
Register
  ↓
Login
  ↓
JWT Token
  ↓
Authorization Header
  ↓
Protected Endpoint
```

## Register

```http
POST /auth/register
```

The user submits registration information.

## Login

```http
POST /auth/login
```

A successful login returns a JWT.

## Using the Token

Protected requests include:

```http
Authorization: Bearer YOUR_JWT_TOKEN
```

## Public vs Protected Endpoints

Read operations can be accessed without authentication.

Write operations require authentication.

Examples of protected operations:

```http
POST /api/disasters
PATCH /api/disasters/{id}
DELETE /api/disasters/{id}
```

## Why JWT?

JWT allows the API to verify that a request is associated with an authenticated user without storing a traditional server-side session for every request.

## Security Notes

Never commit:

* JWT secrets
* API keys
* Database passwords
* `.env` files

Use environment variables for secrets.
