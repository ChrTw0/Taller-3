"""Attendance Service Reports Routes."""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from ..core.database import get_session
from ..schemas.attendance import ErrorResponse
from ..models.attendance import AttendanceStatus, AttendanceSource
from ..services.attendance_service import AttendanceService

router = APIRouter(prefix="/reports", tags=["Attendance Reports"])

@router.get(
    "/attendance-summary",
    response_model=dict,
    summary="Generate Attendance Summary Report",
    description="Generate comprehensive attendance summary for courses and users"
)
async def generate_attendance_summary(
    course_id: Optional[int] = Query(None, description="Filter by course ID"),
    start_date: Optional[datetime] = Query(None, description="Report start date"),
    end_date: Optional[datetime] = Query(None, description="Report end date"),
    db: AsyncSession = Depends(get_session)
):
    """Generate attendance summary report."""

    logger.info(f"📈 ATTENDANCE SUMMARY: course={course_id}, period={start_date} to {end_date}")

    try:
        attendance_service = AttendanceService()

        # Get attendance records
        records, total_records = await attendance_service.get_attendance_records(
            db,
            course_id=course_id,
            start_date=start_date,
            end_date=end_date
        )

        if total_records == 0:
            return {
                "summary": "No attendance records found for the specified criteria",
                "total_records": 0,
                "period": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None
                },
                "statistics": {}
            }

        # Calculate overall statistics
        present_count = len([r for r in records if r.status == AttendanceStatus.PRESENT])
        late_count = len([r for r in records if r.status == AttendanceStatus.LATE])
        absent_count = len([r for r in records if r.status == AttendanceStatus.ABSENT])

        # Group by course
        course_stats = {}
        for record in records:
            course_key = f"{record.course_id}_{record.course_code}"
            if course_key not in course_stats:
                course_stats[course_key] = {
                    "course_id": record.course_id,
                    "course_code": record.course_code,
                    "total": 0,
                    "present": 0,
                    "late": 0,
                    "absent": 0,
                    "unique_students": set()
                }

            course_stats[course_key]["total"] += 1
            course_stats[course_key]["unique_students"].add(record.user_id)

            if record.status == AttendanceStatus.PRESENT:
                course_stats[course_key]["present"] += 1
            elif record.status == AttendanceStatus.LATE:
                course_stats[course_key]["late"] += 1
            elif record.status == AttendanceStatus.ABSENT:
                course_stats[course_key]["absent"] += 1

        # Convert course stats to list format
        course_summary = []
        for course_key, stats in course_stats.items():
            total_course_records = stats["total"]
            attendance_rate = (stats["present"] + stats["late"]) / total_course_records * 100 if total_course_records > 0 else 0
            punctuality_rate = stats["present"] / total_course_records * 100 if total_course_records > 0 else 0

            course_summary.append({
                "course_id": stats["course_id"],
                "course_code": stats["course_code"],
                "total_records": total_course_records,
                "unique_students": len(stats["unique_students"]),
                "present_count": stats["present"],
                "late_count": stats["late"],
                "absent_count": stats["absent"],
                "attendance_rate": round(attendance_rate, 2),
                "punctuality_rate": round(punctuality_rate, 2)
            })

        # Overall statistics
        overall_attendance_rate = (present_count + late_count) / total_records * 100 if total_records > 0 else 0
        overall_punctuality_rate = present_count / total_records * 100 if total_records > 0 else 0

        return {
            "summary": f"Attendance report for {len(course_stats)} course(s)",
            "total_records": total_records,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "overall_statistics": {
                "total_records": total_records,
                "present_count": present_count,
                "late_count": late_count,
                "absent_count": absent_count,
                "attendance_rate": round(overall_attendance_rate, 2),
                "punctuality_rate": round(overall_punctuality_rate, 2)
            },
            "by_course": course_summary
        }

    except Exception as e:
        logger.error(f"❌ Error generating attendance summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get(
    "/daily-attendance/{date}",
    response_model=dict,
    summary="Get Daily Attendance Report",
    description="Get attendance report for a specific date"
)
async def get_daily_attendance_report(
    date: datetime,
    course_id: Optional[int] = Query(None, description="Filter by course ID"),
    db: AsyncSession = Depends(get_session)
):
    """Get daily attendance report."""

    logger.info(f"📅 DAILY REPORT: date={date.date()}, course={course_id}")

    try:
        attendance_service = AttendanceService()

        # Set date range for the specific day
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Get attendance records for the day
        records, total_records = await attendance_service.get_attendance_records(
            db,
            course_id=course_id,
            start_date=start_date,
            end_date=end_date
        )

        if total_records == 0:
            return {
                "date": date.date().isoformat(),
                "message": "No attendance records found for this date",
                "total_records": 0,
                "courses": []
            }

        # Group by course and time
        course_data = {}
        for record in records:
            course_key = record.course_id
            if course_key not in course_data:
                course_data[course_key] = {
                    "course_id": record.course_id,
                    "course_code": record.course_code,
                    "records": [],
                    "stats": {"present": 0, "late": 0, "absent": 0}
                }

            course_data[course_key]["records"].append({
                "user_id": record.user_id,
                "user_code": record.user_code,
                "status": record.status.value,
                "arrival_time": record.actual_arrival.isoformat() if record.actual_arrival else None,
                "classroom": record.classroom_name,
                "distance": float(record.recorded_distance) if record.recorded_distance else None,
                "is_late": record.is_late,
                "minutes_late": record.minutes_late
            })

            # Update stats
            if record.status == AttendanceStatus.PRESENT:
                course_data[course_key]["stats"]["present"] += 1
            elif record.status == AttendanceStatus.LATE:
                course_data[course_key]["stats"]["late"] += 1
            elif record.status == AttendanceStatus.ABSENT:
                course_data[course_key]["stats"]["absent"] += 1

        return {
            "date": date.date().isoformat(),
            "total_records": total_records,
            "total_courses": len(course_data),
            "courses": list(course_data.values())
        }

    except Exception as e:
        logger.error(f"❌ Error generating daily report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get(
    "/gps-events/recent",
    response_model=dict,
    summary="Get Recent GPS Events",
    description="Get recent GPS events for monitoring and debugging"
)
async def get_recent_gps_events(
    limit: int = Query(50, ge=1, le=500, description="Number of events to return"),
    status_filter: Optional[str] = Query(None, description="Filter by event status"),
    db: AsyncSession = Depends(get_session)
):
    """Get recent GPS events for monitoring."""

    logger.info(f"🛰️ RECENT GPS EVENTS: limit={limit}, status={status_filter}")

    try:
        from sqlalchemy import select, desc
        from ..models.attendance import GPSEvent, EventStatus

        query = select(GPSEvent).order_by(desc(GPSEvent.received_at)).limit(limit)

        if status_filter:
            try:
                status_enum = EventStatus(status_filter)
                query = query.where(GPSEvent.status == status_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status filter: {status_filter}"
                )

        result = await db.execute(query)
        events = result.scalars().all()

        events_data = []
        for event in events:
            events_data.append({
                "id": event.id,
                "user_id": event.user_id,
                "user_code": event.user_code,
                "course_id": event.course_id,
                "course_code": event.course_code,
                "latitude": float(event.latitude),
                "longitude": float(event.longitude),
                "accuracy": float(event.accuracy),
                "status": event.status.value,
                "calculated_distance": float(event.calculated_distance) if event.calculated_distance else None,
                "within_range": event.within_range,
                "event_timestamp": event.event_timestamp.isoformat(),
                "received_at": event.received_at.isoformat(),
                "processed_at": event.processed_at.isoformat() if event.processed_at else None,
                "device_type": event.device_type
            })

        return {
            "total_events": len(events_data),
            "status_filter": status_filter,
            "events": events_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting recent GPS events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )