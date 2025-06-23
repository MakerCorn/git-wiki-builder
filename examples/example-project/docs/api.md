# API Documentation

## Overview

The Example Project API provides RESTful endpoints for managing users, projects, and data processing tasks.

## Base URL

```
https://api.example-project.com/v1
```

## Authentication

All API requests require authentication using Bearer tokens:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://api.example-project.com/v1/users
```

## Endpoints

### Users

#### GET /users

List all users.

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com"
    }
  ]
}
```

#### POST /users

Create a new user.

**Request:**
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com"
}
```

### Projects

#### GET /projects

List all projects.

#### POST /projects

Create a new project.

## Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error
