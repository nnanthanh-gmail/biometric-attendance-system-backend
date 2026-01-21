from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from typing import Optional, List
from datetime import date, datetime
from app.api import deps
from app.db.session import get_db
from app.models import Attendance, Schedule, User, CourseRegistration, StudentProfile, LecturerProfile, ClassModel, Subject, Room, Faculty, Major, EducationLevel
from pydantic import BaseModel

router = APIRouter()

# Response models
class AttendanceStats(BaseModel):
    total_students: int
    present_today: int
    absent_today: int
    attendance_rate: float

class DashboardStats(BaseModel):
    total_users: int
    total_students: int
    total_lecturers: int
    total_faculties: int
    total_subjects: int
    total_classes: int
    total_rooms: int

class AttendanceSummary(BaseModel):
    date: date
    total_registered: int
    present: int
    absent: int
    attendance_rate: float

class UserAttendanceRecord(BaseModel):
    attendance_id: str
    time: datetime
    class_name: Optional[str]
    subject_name: Optional[str]
    room_name: Optional[str]
    status: str

class SearchResult(BaseModel):
    schedule_id: str
    date: date
    start_time: str
    end_time: str
    faculty_name: Optional[str]
    major_name: Optional[str]
    education_level_name: Optional[str]
    class_name: Optional[str]
    subject_name: Optional[str]
    room_name: Optional[str]

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """
    API endpoint lấy thống kê tổng quan cơ bản cho dashboard.

    Cung cấp số lượng tổng hợp các thực thể chính trong hệ thống.

    Args:
        db: Session database async

    Returns:
        DashboardStats: Thống kê tổng quan cơ bản
    """
    # Tổng số users
    total_users_result = await db.execute(select(func.count(User.user_id)))
    total_users = total_users_result.scalar() or 0

    # Tổng số students
    total_students_result = await db.execute(select(func.count(StudentProfile.user_id)))
    total_students = total_students_result.scalar() or 0

    # Tổng số lecturers
    total_lecturers_result = await db.execute(select(func.count(LecturerProfile.user_id)))
    total_lecturers = total_lecturers_result.scalar() or 0

    # Tổng số faculties
    from app.models import Faculty
    total_faculties_result = await db.execute(select(func.count(Faculty.faculty_id)))
    total_faculties = total_faculties_result.scalar() or 0

    # Tổng số subjects
    from app.models import Subject
    total_subjects_result = await db.execute(select(func.count(Subject.subject_id)))
    total_subjects = total_subjects_result.scalar() or 0

    # Tổng số classes
    from app.models import ClassModel
    total_classes_result = await db.execute(select(func.count(ClassModel.class_id)))
    total_classes = total_classes_result.scalar() or 0

    # Tổng số rooms
    from app.models import Room
    total_rooms_result = await db.execute(select(func.count(Room.room_id)))
    total_rooms = total_rooms_result.scalar() or 0

    return DashboardStats(
        total_users=total_users,
        total_students=total_students,
        total_lecturers=total_lecturers,
        total_faculties=total_faculties,
        total_subjects=total_subjects,
        total_classes=total_classes,
        total_rooms=total_rooms
    )

@router.get("/attendance/user/{user_id}", response_model=List[UserAttendanceRecord])
async def get_user_attendance_history(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    API endpoint lấy lịch sử điểm danh đầy đủ của người dùng.

    Bao gồm thông tin lớp học, môn học và phòng học từ đăng ký khóa học.

    Args:
        user_id: ID người dùng
        db: Session database async

    Returns:
        List[UserAttendanceRecord]: Danh sách bản ghi điểm danh với thông tin chi tiết
    """
    # Query lấy attendance với thông tin course registration
    query = select(
        Attendance.attendance_id,
        Attendance.time,
        Attendance.status,
        ClassModel.class_name,
        Subject.subject_name,
        Room.room_name
    ).select_from(Attendance).join(
        CourseRegistration, Attendance.user_id == CourseRegistration.user_id
    ).join(
        ClassModel, CourseRegistration.host_class_id == ClassModel.class_id
    ).join(
        Subject, CourseRegistration.subject_id == Subject.subject_id
    ).outerjoin(
        Room, Attendance.room_id == Room.room_id
    ).where(Attendance.user_id == user_id).order_by(Attendance.time.desc())

    result = await db.execute(query)
    records = result.all()

    return [
        UserAttendanceRecord(
            attendance_id=record.attendance_id,
            time=record.time,
            class_name=record.class_name,
            subject_name=record.subject_name,
            room_name=record.room_name,
            status=record.status
        ) for record in records
    ]

@router.get("/search", response_model=List[SearchResult])
async def search_schedules(
    faculty_id: Optional[str] = Query(None, description="ID khoa để lọc"),
    schedule_date: Optional[date] = Query(None, description="Ngày lịch học"),
    major_id: Optional[str] = Query(None, description="ID ngành để lọc"),
    education_level_id: Optional[str] = Query(None, description="ID bậc đào tạo để lọc"),
    db: AsyncSession = Depends(get_db)
):
    """
    API endpoint tìm kiếm lịch học với bộ lọc đa tiêu chí.

    Hỗ trợ lọc theo khoa, ngày, ngành và bậc đào tạo.

    Args:
        faculty_id: ID khoa (tùy chọn)
        schedule_date: Ngày lịch học (tùy chọn)
        major_id: ID ngành (tùy chọn)
        education_level_id: ID bậc đào tạo (tùy chọn)
        db: Session database async

    Returns:
        List[SearchResult]: Danh sách lịch học phù hợp với bộ lọc
    """
    # Import thêm models cần thiết
    from app.models import Faculty, Major, EducationLevel

    # Xây dựng query với joins
    query = select(
        Schedule.schedule_id,
        Schedule.date,
        Schedule.start_time,
        Schedule.end_time,
        Faculty.faculty_name,
        Major.major_name,
        EducationLevel.level_name,
        ClassModel.class_name,
        Subject.subject_name,
        Room.room_name
    ).select_from(Schedule).join(
        ClassModel, Schedule.class_id == ClassModel.class_id
    ).join(
        Subject, Schedule.subject_id == Subject.subject_id
    ).outerjoin(
        Room, Schedule.room_id == Room.room_id
    ).outerjoin(
        Faculty, ClassModel.faculty_id == Faculty.faculty_id
    ).outerjoin(
        Major, ClassModel.major_id == Major.major_id
    ).outerjoin(
        EducationLevel, ClassModel.education_level_id == EducationLevel.level_id
    )

    # Áp dụng filters
    if faculty_id:
        query = query.where(ClassModel.faculty_id == faculty_id)
    if schedule_date:
        query = query.where(Schedule.date == schedule_date)
    if major_id:
        query = query.where(ClassModel.major_id == major_id)
    if education_level_id:
        query = query.where(ClassModel.education_level_id == education_level_id)

    query = query.order_by(Schedule.date.desc(), Schedule.start_time.desc())

    result = await db.execute(query)
    records = result.all()

    return [
        SearchResult(
            schedule_id=record.schedule_id,
            date=record.date,
            start_time=str(record.start_time),
            end_time=str(record.end_time),
            faculty_name=record.faculty_name,
            major_name=record.major_name,
            education_level_name=record.level_name,
            class_name=record.class_name,
            subject_name=record.subject_name,
            room_name=record.room_name
        ) for record in records
    ]

@router.get("/attendance/summary", response_model=List[AttendanceSummary])
async def get_attendance_summary(
    start_date: date = Query(..., description="Ngày bắt đầu"),
    end_date: date = Query(..., description="Ngày kết thúc"),
    class_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Lấy tóm tắt điểm danh theo khoảng thời gian."""
    # Query phức tạp để tính attendance rate theo ngày
    query = text("""
        SELECT
            DATE(a.time) as date,
            COUNT(DISTINCT cr.user_id) as total_registered,
            COUNT(DISTINCT a.user_id) as present,
            ROUND(
                (COUNT(DISTINCT a.user_id) * 100.0 / COUNT(DISTINCT cr.user_id)),
                2
            ) as attendance_rate
        FROM course_registration cr
        LEFT JOIN attendance a ON cr.user_id = a.user_id
            AND DATE(a.time) = DATE(cr.created_at)
        WHERE DATE(cr.created_at) BETWEEN :start_date AND :end_date
        """ + (" AND cr.class_id = :class_id" if class_id else "") + """
        GROUP BY DATE(a.time)
        ORDER BY date
    """)

    params = {"start_date": start_date, "end_date": end_date}
    if class_id:
        params["class_id"] = class_id

    result = await db.execute(query, params)
    rows = result.fetchall()

    summary = []
    for row in rows:
        absent = row.total_registered - row.present
        summary.append(AttendanceSummary(
            date=row.date,
            total_registered=row.total_registered,
            present=row.present,
            absent=absent,
            attendance_rate=row.attendance_rate or 0
        ))

    return summary

@router.get("/attendance/user/{user_id}")
async def get_user_attendance(
    user_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db)
):
    """Lấy lịch sử điểm danh của một user."""
    query = select(Attendance).where(Attendance.user_id == user_id)

    if start_date:
        query = query.where(func.date(Attendance.time) >= start_date)
    if end_date:
        query = query.where(func.date(Attendance.time) <= end_date)

    query = query.order_by(Attendance.time.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/schedules/calendar")
async def get_schedules_calendar(
    start_date: date = Query(..., description="Ngày bắt đầu"),
    end_date: date = Query(..., description="Ngày kết thúc"),
    lecturer_id: Optional[str] = None,
    class_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Lấy lịch trình theo dạng calendar (cho frontend calendar view)."""
    query = select(Schedule).where(
        and_(
            Schedule.learn_date >= start_date,
            Schedule.learn_date <= end_date
        )
    )

    if lecturer_id:
        query = query.where(Schedule.lecturer_id == lecturer_id)
    if class_id:
        query = query.where(Schedule.class_id == class_id)

    query = query.order_by(Schedule.learn_date, Schedule.start_period)
    result = await db.execute(query)
    schedules = result.scalars().all()

    # Format for calendar view
    calendar_events = []
    for schedule in schedules:
        calendar_events.append({
            "id": schedule.schedule_id,
            "title": f"Lớp {schedule.class_id}",
            "start": f"{schedule.learn_date}T{schedule.start_period:02d}:00:00",
            "end": f"{schedule.learn_date}T{schedule.end_period:02d}:00:00",
            "extendedProps": {
                "subject_id": schedule.subject_id,
                "room_id": schedule.room_id,
                "lecturer_id": schedule.lecturer_id,
                "class_id": schedule.class_id
            }
        })

    return calendar_events

@router.get("/search")
async def search_entities(
    q: str = Query(..., description="Từ khóa tìm kiếm"),
    entity_type: str = Query(..., description="Loại entity: users, students, lecturers, classes, subjects"),
    limit: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """API tìm kiếm tổng hợp."""
    if entity_type == "users":
        query = select(User).where(
            or_(
                User.user_id.ilike(f"%{q}%"),
                User.full_name.ilike(f"%{q}%")
            )
        )
        if limit:
            query = query.limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    elif entity_type == "students":
        query = select(StudentProfile).where(
            or_(
                StudentProfile.user_id.ilike(f"%{q}%"),
                StudentProfile.full_name.ilike(f"%{q}%")
            )
        )
        if limit:
            query = query.limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    elif entity_type == "lecturers":
        query = select(LecturerProfile).where(
            or_(
                LecturerProfile.user_id.ilike(f"%{q}%"),
                LecturerProfile.full_name.ilike(f"%{q}%")
            )
        )
        if limit:
            query = query.limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    elif entity_type == "classes":
        query = select(ClassModel).where(
            ClassModel.class_id.ilike(f"%{q}%")
        )
        if limit:
            query = query.limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    elif entity_type == "subjects":
        from app.models import Subject
        query = select(Subject).where(
            or_(
                Subject.subject_id.ilike(f"%{q}%"),
                Subject.subject_name.ilike(f"%{q}%")
            )
        )
        if limit:
            query = query.limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    return []