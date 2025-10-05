"""Course Service Routers package."""

from .courses import router as courses_router
from .classrooms import router as classrooms_router
from .course_classrooms import router as course_classrooms_router
from .enrollments import router as enrollments_router
from .schedules import router as schedules_router

__all__ = ["courses_router", "classrooms_router", "course_classrooms_router", "enrollments_router", "schedules_router"]