# APIs Explained Using Epicenter

## What Is an API?

An API is a way for two software systems to communicate.

Instead of one application directly accessing another application's internal code or database, it sends a request to an API.

```text
Application A
     ↓
    API
     ↓
Application B
```

## Example

Epicenter exposes:

```http
GET /api/disasters
```

A client can request disaster data through this endpoint.

```text
Frontend
   ↓
GET /api/disasters
   ↓
FastAPI
   ↓
PostgreSQL
   ↓
JSON
   ↓
Frontend
```

## HTTP Methods

Common HTTP methods include:

| Method | Purpose       |
| ------ | ------------- |
| GET    | Retrieve data |
| POST   | Create data   |
| PATCH  | Update data   |
| DELETE | Delete data   |

Epicenter uses these methods for its REST API.

## Example GET Request

```http
GET /api/disasters?category=Earthquake
```

The server processes the request and returns structured data.

## Why JSON?

APIs commonly return JSON because it is easy for applications to parse.

Example:

```json
{
  "id": 1,
  "name": "Example Earthquake",
  "category": "Earthquake"
}
```

A frontend can read these fields and display them to the user.

## The Key Idea

The API acts as a contract between the frontend and backend.

The frontend does not need to know how PostgreSQL works.

It only needs to know:

```text
Where to send the request
What parameters are accepted
What response to expect
```

That separation makes applications easier to build and integrate.
