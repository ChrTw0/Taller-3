# 📚 Course Service - GeoAttend System

Independent microservice for academic course and classroom management.

## 🚀 Features

- ✅ Course creation and management
- ✅ **GPS classroom coordinates** (for Attendance Service)
- ✅ Student enrollment management
- ✅ Academic scheduling
- ✅ Detection radius configuration per course
- ✅ Teacher validation via User Service
- ✅ RESTful API with FastAPI
- ✅ Async PostgreSQL with SQLAlchemy 2.0
- ✅ Inter-service communication

## 🏗️ Architecture

This service manages the **academic domain**:
- **Independent deployment**
- **Own database schema** (`course_schema`)
- **GPS coordinates provider** for attendance validation
- **No shared dependencies**

## 📋 API Endpoints

### Course Management
- `POST /api/v1/courses/` - Create course
- `GET /api/v1/courses/` - List courses (with filters)
- `GET /api/v1/courses/{id}` - Get course details
- `GET /api/v1/courses/code/{code}` - Get course by code
- `PUT /api/v1/courses/{id}` - Update course
- `DELETE /api/v1/courses/{id}` - Deactivate course

### GPS Coordinates (Special for Attendance Service)
- `GET /api/v1/courses/{id}/coordinates` - **Get GPS coordinates**

### Classroom Management
- `POST /api/v1/classrooms/course/{course_id}` - Add classroom
- `GET /api/v1/classrooms/course/{course_id}` - Get course classrooms

### Enrollment Management
- `POST /api/v1/enrollments/course/{course_id}` - Enroll student
- `GET /api/v1/enrollments/course/{course_id}` - Get course enrollments
- `GET /api/v1/enrollments/student/{student_id}` - Get student enrollments

### System
- `GET /health` - Health check
- `GET /` - Service info

## 🗺️ GPS Coordinates Response

**Special endpoint for Attendance Service:**

```bash
GET /api/v1/courses/123/coordinates
```

```json
{
  "course_id": 123,
  "course_code": "CS101",
  "detection_radius": 2.0,
  "classrooms": [
    {
      "id": 1,
      "latitude": -12.0464,
      "longitude": -77.0428,
      "building": "Edificio A",
      "room_number": "101"
    }
  ]
}
```

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
CREATE SCHEMA IF NOT EXISTS course_schema;
```

4. **Run the service:**
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload
```

### Docker

```bash
# Build image
docker build -t course-service .

# Run container
docker run -d -p 8002:8002 --env-file .env course-service
```

## 🔧 Configuration

Key environment variables:

- `SERVICE_PORT` - Service port (default: 8002)
- `DATABASE_URL` - PostgreSQL connection string
- `DATABASE_SCHEMA` - Database schema (course_schema)
- `DEFAULT_DETECTION_RADIUS` - GPS detection radius (meters)
- `USER_SERVICE_URL` - User Service endpoint for validation

## 🧪 Testing

### Manual Testing

1. **Create a course:**
```bash
curl -X POST "http://localhost:8002/api/v1/courses/" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "CS101",
    "name": "Introduction to Computer Science",
    "description": "Basic programming concepts",
    "credits": 3,
    "academic_year": "2024",
    "semester": "A",
    "teacher_id": 1,
    "teacher_code": "PROF001",
    "max_students": 30,
    "detection_radius": 2.5
  }'
```

2. **Add classroom with GPS:**
```bash
curl -X POST "http://localhost:8002/api/v1/classrooms/course/1" \
  -H "Content-Type: application/json" \
  -d '{
    "building": "Edificio A",
    "room_number": "101",
    "floor": 1,
    "latitude": -12.0464,
    "longitude": -77.0428,
    "capacity": 35
  }'
```

3. **Get coordinates (for Attendance Service):**
```bash
curl -X GET "http://localhost:8002/api/v1/courses/1/coordinates"
```

### API Documentation

When running in debug mode, visit:
- Swagger UI: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc

## 📊 Database Schema

### courses table (course_schema.courses)
- `id` (PK) - Course ID
- `code` - Unique course code
- `name` - Course name
- `teacher_id` - Reference to User Service
- `detection_radius` - GPS detection radius (meters)
- `max_students` - Enrollment limit

### classrooms table (course_schema.classrooms)
- `id` (PK) - Classroom ID
- `course_id` (FK) - Course reference
- `building` - Building name
- `room_number` - Room identifier
- `latitude` - GPS latitude coordinate
- `longitude` - GPS longitude coordinate
- `capacity` - Room capacity

### enrollments table (course_schema.enrollments)
- `id` (PK) - Enrollment ID
- `course_id` (FK) - Course reference
- `student_id` - Reference to User Service
- `status` - Enrollment status

## 🔗 Inter-service Communication

This service communicates with:
- **User Service** (8001) - Teacher/student validation
- **Attendance Service** (8003) - Provides GPS coordinates

## 🐳 Production Deployment

The service is designed for independent deployment:

1. **Environment-based configuration**
2. **Health checks** for monitoring
3. **Structured logging**
4. **Database schema isolation**

## 📈 Monitoring

- Health endpoint: `/health`
- Structured logging with loguru
- Database connection monitoring
- Inter-service call tracking