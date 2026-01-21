"""
Endpoints quản lý đăng ký khóa học.

Cung cấp CRUD operations cho course registrations, bao gồm tạo, đọc, cập nhật và xóa bản ghi đăng ký.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.api import deps
from app.db.session import get_db
from app.models import CourseRegistration, User, Subject, ClassModel
from app.schemas import CourseRegCreate, CourseRegResponse

router = APIRouter()

@router.get("/", response_model=list[CourseRegResponse])
async def read_course_registrations(skip: int = 0, limit: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    Lấy danh sách đăng ký khóa học với pagination.

    Args:
        skip: Số bản ghi bỏ qua.
        limit: Số bản ghi tối đa trả về.
        db: Database session.

    Returns:
        Danh sách các CourseRegResponse objects.
    """
    query = select(CourseRegistration).offset(skip)
    if limit:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{reg_id}", response_model=CourseRegResponse)
async def read_course_registration(reg_id: int, db: AsyncSession = Depends(get_db)):
    """
    Lấy bản ghi đăng ký khóa học theo ID.

    Args:
        reg_id: ID duy nhất của bản ghi đăng ký.
        db: Database session.

    Returns:
        CourseRegResponse object.

    Raises:
        HTTPException: Nếu bản ghi không tồn tại.
    """
    result = await db.execute(select(CourseRegistration).where(CourseRegistration.reg_id == reg_id))
    reg = result.scalars().first()
    if not reg:
        raise HTTPException(status_code=404, detail="Course registration not found")
    return reg

@router.get("/user/{user_id}", response_model=list[CourseRegResponse])
async def read_course_registrations_by_user(user_id: str, skip: int = 0, limit: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    API endpoint lấy danh sách đăng ký khóa học theo người dùng với phân trang offset/limit.

    Hỗ trợ phân trang bằng offset/limit để tối ưu hiệu suất.

    Args:
        user_id: ID người dùng
        skip: Số bản ghi bỏ qua (offset)
        limit: Số lượng bản ghi tối đa trả về
        db: Session database async

    Returns:
        List[CourseRegResponse]: Danh sách đăng ký khóa học của người dùng
    """
    query = select(CourseRegistration).where(CourseRegistration.user_id == user_id).order_by(CourseRegistration.reg_id.asc()).offset(skip)
    if limit:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/subject/{subject_id}", response_model=list[CourseRegResponse])
async def read_course_registrations_by_subject(subject_id: str, skip: int = 0, limit: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    API endpoint lấy danh sách đăng ký khóa học theo môn học với phân trang offset/limit.

    Hỗ trợ phân trang bằng offset/limit để tối ưu hiệu suất.

    Args:
        subject_id: ID môn học
        skip: Số bản ghi bỏ qua (offset)
        limit: Số lượng bản ghi tối đa trả về
        db: Session database async

    Returns:
        List[CourseRegResponse]: Danh sách đăng ký khóa học của môn học
    """
    query = select(CourseRegistration).where(CourseRegistration.subject_id == subject_id).order_by(CourseRegistration.reg_id.asc()).offset(skip)
    if limit:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/class/{class_id}", response_model=list[CourseRegResponse])
async def read_course_registrations_by_class(class_id: str, skip: int = 0, limit: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    API endpoint lấy danh sách đăng ký khóa học theo lớp học với phân trang offset/limit.

    Hỗ trợ phân trang bằng offset/limit để tối ưu hiệu suất.

    Args:
        class_id: ID lớp học
        skip: Số bản ghi bỏ qua (offset)
        limit: Số lượng bản ghi tối đa trả về
        db: Session database async

    Returns:
        List[CourseRegResponse]: Danh sách đăng ký khóa học của lớp học
    """
    query = select(CourseRegistration).where(CourseRegistration.host_class_id == class_id).order_by(CourseRegistration.reg_id.asc()).offset(skip)
    if limit:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=CourseRegResponse)
async def create_course_registration(reg_in: CourseRegCreate, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """
    Tạo bản ghi đăng ký khóa học mới. Yêu cầu admin authentication.

    Args:
        reg_in: Dữ liệu tạo đăng ký.
        db: Database session.
        _: Admin authentication dependency.

    Returns:
        CourseRegResponse object đã tạo.

    Raises:
        HTTPException: Nếu user, subject hoặc class không tồn tại.
    """
    # Validate FK
    if not await db.get(User, reg_in.user_id):
        raise HTTPException(status_code=400, detail="User not found")
    if not await db.get(Subject, reg_in.subject_id):
        raise HTTPException(status_code=400, detail="Subject not found")
    if not await db.get(ClassModel, reg_in.host_class_id):
        raise HTTPException(status_code=400, detail="Class not found")
    
    obj = CourseRegistration(**reg_in.dict())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

@router.put("/{reg_id}", response_model=CourseRegResponse)
async def update_course_registration(reg_id: int, reg_in: CourseRegCreate, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """
    Cập nhật bản ghi đăng ký khóa học. Yêu cầu admin authentication.

    Args:
        reg_id: ID của bản ghi cần cập nhật.
        reg_in: Dữ liệu cập nhật.
        db: Database session.
        _: Admin authentication dependency.

    Returns:
        CourseRegResponse object đã cập nhật.

    Raises:
        HTTPException: Nếu bản ghi không tồn tại hoặc cập nhật thất bại.
    """
    existing = await db.get(CourseRegistration, reg_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Course registration not found")
    
    update_data = reg_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing, field, value)
    
    try:
        await db.commit()
        await db.refresh(existing)
        return existing
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi cập nhật: {str(e)}")

@router.delete("/{reg_id}")
async def delete_course_registration(reg_id: int, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """
    Xóa bản ghi đăng ký khóa học. Yêu cầu admin authentication.

    Args:
        reg_id: ID của bản ghi cần xóa.
        db: Database session.
        _: Admin authentication dependency.

    Returns:
        Thông báo thành công.

    Raises:
        HTTPException: Nếu bản ghi không tồn tại.
    """
    existing = await db.get(CourseRegistration, reg_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Course registration not found")
    await db.delete(existing)
    await db.commit()
    return {"message": f"Đã xóa đăng ký khóa học {reg_id}"}