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
async def get_user_attendance_history(
    user_id: str,
    start_date: Optional[date] = Query(None, description="Ngày bắt đầu lọc"),
    end_date: Optional[date] = Query(None, description="Ngày kết thúc lọc"),
    db: AsyncSession = Depends(get_db)
):
    """
    API endpoint lấy lịch sử điểm danh đầy đủ của người dùng.

    Bao gồm thông tin lớp học, môn học và phòng học từ lịch trình.
    Hỗ trợ lọc theo khoảng thời gian.

    Args:
        user_id: ID người dùng
        start_date: Ngày bắt đầu (optional)
        end_date: Ngày kết thúc (optional)
        db: Session database async

    Returns:
        List[UserAttendanceRecord]: Danh sách bản ghi điểm danh với thông tin chi tiết
    """
    # Sửa join: Attendance -> Schedule -> Subject, Room, ClassModel
    # Loại bỏ join với CourseRegistration vì không cần thiết cho lịch sử điểm danh
    query = select(
        Attendance.attend_id,
        Attendance.attend_time,
        Attendance.status,
        ClassModel.class_name,
        Subject.subject_name,
        Room.room_name
    ).select_from(Attendance).join(
        Schedule, Attendance.schedule_id == Schedule.schedule_id
    ).join(
        ClassModel, Schedule.class_id == ClassModel.class_id
    ).join(
        Subject, Schedule.subject_id == Subject.subject_id
    ).outerjoin(
        Room, Schedule.room_id == Room.room_id
    ).where(Attendance.user_id == user_id)

    # Thêm filter thời gian nếu có
    if start_date:
        query = query.where(func.date(Attendance.attend_time) >= start_date)
    if end_date:
        query = query.where(func.date(Attendance.attend_time) <= end_date)

    query = query.order_by(Attendance.attend_time.desc())

    result = await db.execute(query)
    records = result.all()

    return [
        UserAttendanceRecord(
            attendance_id=str(record.attend_id),
            time=record.attend_time,
            class_name=record.class_name,
            subject_name=record.subject_name,
            room_name=record.room_name,
            status="Có mặt" if record.status else "Vắng mặt"
        ) for record in records
    ]

@router.get("/search")
async def search_entities(
    q: str = Query(..., description="Từ khóa tìm kiếm"),
    entity_type: str = Query(..., description="Loại thực thể: users, students, lecturers, classes, subjects"),
    limit: Optional[int] = Query(50, description="Số lượng kết quả tối đa"),
    db: AsyncSession = Depends(get_db)
):
    """
    API endpoint tìm kiếm tổng hợp theo từ khóa trong các thực thể.

    Hỗ trợ tìm kiếm không phân biệt chữ hoa/thường với ILIKE.

    Args:
        q: Từ khóa tìm kiếm
        entity_type: Loại thực thể cần tìm
        limit: Số lượng kết quả tối đa (mặc định 50)
        db: Session database async

    Returns:
        List: Danh sách kết quả tìm kiếm
    """
    if entity_type == "users":
        # Tìm kiếm trong bảng users
        query = select(User).where(
            or_(
                User.user_id.ilike(f"%{q}%"),
                User.full_name.ilike(f"%{q}%")
            )
        ).limit(limit)
        result = await db.execute(query)
        users = result.scalars().all()
        return [
            {
                "id": user.user_id,
                "name": user.full_name,
                "type": "user"
            } for user in users
        ]

    elif entity_type == "students":
        # Tìm kiếm trong student profiles với join User
        # Loại bỏ student_code vì không tồn tại trong schema
        query = select(StudentProfile, User.full_name).join(User, StudentProfile.user_id == User.user_id).where(
            or_(
                StudentProfile.user_id.ilike(f"%{q}%"),
                User.full_name.ilike(f"%{q}%")
            )
        ).limit(limit)
        result = await db.execute(query)
        students = result.all()
        return [
            {
                "id": student.user_id,
                "name": name,
                "type": "student"
            } for student, name in students
        ]

    elif entity_type == "lecturers":
        # Tìm kiếm trong lecturer profiles với join User
        # Loại bỏ lecturer_code vì không tồn tại trong schema
        query = select(LecturerProfile, User.full_name).join(User, LecturerProfile.user_id == User.user_id).where(
            or_(
                LecturerProfile.user_id.ilike(f"%{q}%"),
                User.full_name.ilike(f"%{q}%")
            )
        ).limit(limit)
        result = await db.execute(query)
        lecturers = result.all()
        return [
            {
                "id": lecturer.user_id,
                "name": name,
                "type": "lecturer"
            } for lecturer, name in lecturers
        ]

    elif entity_type == "classes":
        # Tìm kiếm trong classes
        query = select(ClassModel).where(
            or_(
                ClassModel.class_id.ilike(f"%{q}%"),
                ClassModel.class_name.ilike(f"%{q}%")
            )
        ).limit(limit)
        result = await db.execute(query)
        classes = result.scalars().all()
        return [
            {
                "id": cls.class_id,
                "name": cls.class_name,
                "type": "class"
            } for cls in classes
        ]

    elif entity_type == "subjects":
        # Tìm kiếm trong subjects
        # Loại bỏ subject_code vì không tồn tại trong schema
        query = select(Subject).where(
            or_(
                Subject.subject_id.ilike(f"%{q}%"),
                Subject.subject_name.ilike(f"%{q}%")
            )
        ).limit(limit)
        result = await db.execute(query)
        subjects = result.scalars().all()
        return [
            {
                "id": subject.subject_id,
                "name": subject.subject_name,
                "type": "subject"
            } for subject in subjects
        ]

    # Nếu entity_type không hợp lệ
    return []

@router.get("/attendance/summary", response_model=List[AttendanceSummary])
async def get_attendance_summary(
    start_date: date = Query(..., description="Ngày bắt đầu"),
    end_date: date = Query(..., description="Ngày kết thúc"),
    class_id: Optional[str] = Query(None, description="ID lớp học (optional)"),
    lecturer_id: Optional[str] = Query(None, description="ID giảng viên (optional)"),
    subject_id: Optional[str] = Query(None, description="ID môn học (optional)"),
    db: AsyncSession = Depends(get_db)
):
    """Lấy tóm tắt điểm danh theo khoảng thời gian, lọc theo lớp, giảng viên, môn học."""
    # Sửa query: join schedule với course_registration và attendance
    # Thêm filter lecturer_id, subject_id để lọc "của ai" (giảng viên), "môn nào" (subject)
    query = text("""
        SELECT
            s.learn_date as date,
            COUNT(DISTINCT cr.user_id) as total_registered,
            COUNT(DISTINCT a.user_id) as present,
            ROUND(
                (COUNT(DISTINCT a.user_id) * 100.0 / NULLIF(COUNT(DISTINCT cr.user_id), 0)),
                2
            ) as attendance_rate
        FROM schedule s
        LEFT JOIN course_registration cr ON s.class_id = cr.host_class_id AND s.subject_id = cr.subject_id
        LEFT JOIN attendance a ON s.schedule_id = a.schedule_id
        WHERE s.learn_date BETWEEN :start_date AND :end_date
        """ + (" AND s.class_id = :class_id" if class_id else "") + """
        """ + (" AND s.lecturer_id = :lecturer_id" if lecturer_id else "") + """
        """ + (" AND s.subject_id = :subject_id" if subject_id else "") + """
        GROUP BY s.learn_date
        ORDER BY s.learn_date
    """)

    params = {"start_date": start_date, "end_date": end_date}
    if class_id:
        params["class_id"] = class_id
    if lecturer_id:
        params["lecturer_id"] = lecturer_id
    if subject_id:
        params["subject_id"] = subject_id

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

@router.get("/attendance/raw/user/{user_id}")
async def get_user_attendance_raw(
    user_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db)
):
    """Lấy lịch sử điểm danh thô của một user."""
    # Sửa Attendance.time thành Attendance.attend_time
    query = select(Attendance).where(Attendance.user_id == user_id)

    if start_date:
        query = query.where(func.date(Attendance.attend_time) >= start_date)
    if end_date:
        query = query.where(func.date(Attendance.attend_time) <= end_date)

    query = query.order_by(Attendance.attend_time.desc())
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