# Diagramas de Arquitectura - GeoAttend System

## 1. Diagrama de Arquitectura General (C4 - Nivel 1)

```
┌─────────────────────────────────────────────────────────────┐
│                    GeoAttend System                         │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Mobile    │    │     Web     │    │   Admin     │     │
│  │    App      │    │  Dashboard  │    │   Panel     │     │
│  │ (Android)   │    │  (React)    │    │             │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                   │                   │          │
│         └───────────────────┼───────────────────┘          │
│                             │                              │
│                    ┌─────────────┐                         │
│                    │ API Gateway │                         │
│                    │   (8080)    │                         │
│                    └─────────────┘                         │
│                             │                              │
│    ┌────────────────────────┼────────────────────────┐     │
│    │                        │                        │     │
│ ┌─────────┐         ┌─────────────┐         ┌─────────────┐ │
│ │  User   │         │   Course    │         │ Attendance  │ │
│ │Service  │         │  Service    │         │   Service   │ │
│ │ (8081)  │         │   (8082)    │         │   (8083)    │ │
│ └─────────┘         └─────────────┘         └─────────────┘ │
│    │                        │                        │     │
│    └────────────────────────┼────────────────────────┘     │
│                             │                              │
│                    ┌─────────────┐                         │
│                    │ PostgreSQL  │                         │
│                    │   (5432)    │                         │
│                    └─────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

## 2. Diagrama de Componentes (C4 - Nivel 2)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           API Gateway (8080)                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Router    │  │   Auth      │  │Rate Limiter │  │Load Balancer│    │
│  │   Filter    │  │   Filter    │  │   Filter    │  │   Filter    │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
           │                        │                        │
           ▼                        ▼                        ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  User Service   │      │ Course Service  │      │Attendance Service│
│     (8081)      │      │     (8082)      │      │     (8083)      │
│                 │      │                 │      │                 │
│ ┌─────────────┐ │      │ ┌─────────────┐ │      │ ┌─────────────┐ │
│ │   Auth      │ │      │ │   Course    │ │      │ │   GPS       │ │
│ │ Controller  │ │      │ │ Controller  │ │      │ │ Processor   │ │
│ └─────────────┘ │      │ └─────────────┘ │      │ └─────────────┘ │
│ ┌─────────────┐ │      │ ┌─────────────┐ │      │ ┌─────────────┐ │
│ │   User      │ │      │ │Coordinates  │ │      │ │ Distance    │ │
│ │ Controller  │ │      │ │   Service   │ │      │ │ Calculator  │ │
│ └─────────────┘ │      │ └─────────────┘ │      │ └─────────────┘ │
│ ┌─────────────┐ │      │ ┌─────────────┐ │      │ ┌─────────────┐ │
│ │    JWT      │ │      │ │   Schedule  │ │      │ │ Attendance  │ │
│ │  Service    │ │      │ │   Service   │ │      │ │   Record    │ │
│ └─────────────┘ │      │ └─────────────┘ │      │ └─────────────┘ │
│ ┌─────────────┐ │      │ ┌─────────────┐ │      │ ┌─────────────┐ │
│ │User Repository│ │      │Course Repository│ │      │Event Repository│ │
│ └─────────────┘ │      │ └─────────────┘ │      │ └─────────────┘ │
└─────────────────┘      └─────────────────┘      └─────────────────┘
           │                        │                        │
           ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            PostgreSQL Database                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │user_schema  │  │course_schema│  │attendance   │  │notification │    │
│  │             │  │             │  │  _schema    │  │  _schema    │    │
│  │- users      │  │- courses    │  │- events     │  │- messages   │    │
│  │- roles      │  │- classrooms │  │- attendance │  │- templates  │    │
│  │- profiles   │  │- schedules  │  │- reports    │  │             │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

## 3. Flujo de Datos - Registro de Asistencia

```
┌─────────────┐    1. GPS Event      ┌─────────────────┐
│   Mobile    │ ─────────────────────▶│   API Gateway   │
│     App     │                      │     (8080)      │
└─────────────┘                      └─────────────────┘
                                               │
                                               │ 2. Route to
                                               │    Attendance Service
                                               ▼
                                     ┌─────────────────┐
                                     │  Attendance     │
                                     │   Service       │
                                     │   (8083)        │
                                     └─────────────────┘
                                               │
                                               │ 3. Validate GPS
                                               │    coordinates
                                               ▼
                                     ┌─────────────────┐
                                     │ Distance        │
                                     │ Calculator      │
                                     │ (Haversine)     │
                                     └─────────────────┘
                                               │
                                               │ 4. If distance ≤ 2m
                                               ▼
┌─────────────┐    8. Notification   ┌─────────────────┐
│   Mobile    │ ◀─────────────────── │   PostgreSQL    │
│     App     │                      │   Database      │
└─────────────┘                      └─────────────────┘
       ▲                                       ▲
       │                                       │
       │ 7. Push Notification                  │ 5. Record
       │                                       │    Attendance
┌─────────────────┐                           │
│ Notification    │ ◀─────────────────────────┘
│   Service       │   6. Attendance Event
│   (8084)        │
└─────────────────┘
```

## 4. Diagrama de Secuencia - Proceso de Autenticación

```
Mobile App    API Gateway    User Service    PostgreSQL
    │              │              │             │
    │──login()────▶│              │             │
    │              │──validate───▶│             │
    │              │              │──query─────▶│
    │              │              │◀─user──────│
    │              │◀─JWT token───│             │
    │◀─response────│              │             │
    │              │              │             │
    │──api call───▶│              │             │
    │ (with JWT)   │──verify─────▶│             │
    │              │◀─valid──────│             │
    │              │──forward────▶│             │
    │              │              │ (to target  │
    │              │              │  service)   │
```

## 5. Diagrama de Deployment

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            Docker Host                                  │
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   eureka    │  │api-gateway  │  │user-service │  │course-service│   │
│  │   :8761     │  │   :8080     │  │   :8081     │  │   :8082     │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │attendance   │  │notification │  │ postgresql  │  │   nginx     │    │
│  │  :8083      │  │   :8084     │  │   :5432     │  │   :80       │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                              Internet/Users
                                     │
                                ┌─────────┐
                                │ Browser │
                                └─────────┘
                                ┌─────────┐
                                │ Mobile  │
                                │   App   │
                                └─────────┘
```

## 6. Diagrama de Base de Datos

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PostgreSQL Database                             │
│                                                                         │
│  user_schema                 course_schema              attendance_schema│
│  ┌─────────────┐           ┌─────────────┐             ┌─────────────┐   │
│  │    users    │           │   courses   │             │   events    │   │
│  │─────────────│           │─────────────│             │─────────────│   │
│  │ id (PK)     │           │ id (PK)     │             │ id (PK)     │   │
│  │ code        │           │ name        │             │ student_code│   │
│  │ name        │           │ section     │             │ course_id   │   │
│  │ email       │           │ latitude    │             │ latitude    │   │
│  │ password    │           │ longitude   │             │ longitude   │   │
│  │ role        │           │ altitude    │             │ accuracy    │   │
│  │ status      │           │ radius      │             │ timestamp   │   │
│  │ created_at  │           │ schedule    │             │ status      │   │
│  └─────────────┘           │ professor_id│             └─────────────┘   │
│         │                  │ created_at  │                    │        │
│         │                  └─────────────┘                    │        │
│         │                         │                          │        │
│  ┌─────────────┐                 │                   ┌─────────────┐   │
│  │   roles     │                 │                   │ attendance  │   │
│  │─────────────│                 │                   │─────────────│   │
│  │ id (PK)     │                 │                   │ id (PK)     │   │
│  │ name        │                 │                   │ event_id    │   │
│  │ permissions │                 │                   │ student_code│   │
│  └─────────────┘                 │                   │ course_id   │   │
│                                   │                   │ status      │   │
│  ┌─────────────┐           ┌─────────────┐            │ source      │   │
│  │course_enrolls│          │ classrooms  │            │ registered_at│  │
│  │─────────────│           │─────────────│            └─────────────┘   │
│  │ id (PK)     │           │ id (PK)     │                            │
│  │ student_code│           │ name        │                            │
│  │ course_id   │           │ building    │                            │
│  │ enrolled_at │           │ floor       │                            │
│  └─────────────┘           │ capacity    │                            │
│                            └─────────────┘                            │
└─────────────────────────────────────────────────────────────────────────┘
```

## 7. Diagrama de Comunicación entre Servicios

```
                    ┌─────────────────┐
                    │   API Gateway   │
                    │     (8080)      │
                    └─────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
   │    User     │ │   Course    │ │ Attendance  │
   │  Service    │ │  Service    │ │  Service    │
   │   (8081)    │ │   (8082)    │ │   (8083)    │
   └─────────────┘ └─────────────┘ └─────────────┘
            │               │               │
            │               │               │ Event Bus
            │               │               │ (Optional)
            │               │               ▼
            │               │      ┌─────────────┐
            │               │      │Notification │
            │               │      │  Service    │
            │               │      │   (8084)    │
            │               │      └─────────────┘
            │               │
            └───────────────┼───────────────┘
                            │
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │     (5432)      │
                    └─────────────────┘
                            │
                    ┌─────────────────┐
                    │ Eureka Server   │
                    │     (8761)      │
                    └─────────────────┘
```

Este conjunto de diagramas proporciona una visión completa de la arquitectura del sistema GeoAttend, desde la vista de alto nivel hasta los detalles de implementación y comunicación entre componentes.