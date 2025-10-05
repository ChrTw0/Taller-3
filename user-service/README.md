# 🔐 User Service - GeoAttend System

Independent microservice for user authentication and management.

## 🚀 Features

- ✅ User registration and authentication
- ✅ JWT token-based security
- ✅ Password hashing with bcrypt
- ✅ Role-based access control (student, teacher, admin)
- ✅ RESTful API with FastAPI
- ✅ Async PostgreSQL with SQLAlchemy 2.0
- ✅ Comprehensive data validation with Pydantic
- ✅ Health checks and monitoring

## 🏗️ Architecture

This service follows microservices best practices:
- **Independent deployment**
- **Own database schema** (`user_schema`)
- **No shared dependencies**
- **Self-contained authentication**

## 📋 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/refresh` - Refresh token

### User Management
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update current user
- `GET /api/v1/users/{user_id}` - Get user by ID (public info)
- `GET /api/v1/users/code/{code}` - Get user by code
- `GET /api/v1/users/` - List users (admin only)
- `DELETE /api/v1/users/{user_id}` - Deactivate user (admin only)

### System
- `GET /health` - Health check
- `GET /` - Service info

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 12+

### Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Create database schema:**
```sql
CREATE SCHEMA IF NOT EXISTS user_schema;
```

4. **Run the service:**
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

### Docker

```bash
# Build image
docker build -t user-service .

# Run container
docker run -d -p 8001:8001 --env-file .env user-service
```

## 🔧 Configuration

Key environment variables:

- `SERVICE_PORT` - Service port (default: 8001)
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time

## 🧪 Testing

### Manual Testing

1. **Create a user:**
```bash
curl -X POST "http://localhost:8001/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "STU001",
    "email": "student@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student"
  }'
```

2. **Login:**
```bash
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "SecurePass123!"
  }'
```

3. **Access protected endpoint:**
```bash
curl -X GET "http://localhost:8001/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### API Documentation

When running in debug mode, visit:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## 📊 Database Schema

### users table (user_schema.users)
- `id` (PK) - User ID
- `code` - Unique user code
- `email` - User email (unique)
- `hashed_password` - Bcrypt password hash
- `first_name` - First name
- `last_name` - Last name
- `role` - User role (student/teacher/admin)
- `is_active` - Account status
- `is_verified` - Email verification status
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

## 🔗 Inter-service Communication

This service can communicate with:
- **Course Service** (8002) - User enrollment validation
- **Attendance Service** (8003) - User attendance records

Communication is done via HTTP REST APIs.

## 🐳 Production Deployment

The service is designed to be deployed independently:

1. **Environment variables** for configuration
2. **Health checks** for monitoring
3. **Structured logging** for observability
4. **Graceful shutdown** handling

## 📈 Monitoring

- Health endpoint: `/health`
- Structured logging with loguru
- Request/response logging
- Error tracking