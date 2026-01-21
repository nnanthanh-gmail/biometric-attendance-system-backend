"""
Module quản lý API endpoints cho thực thể Class (Lớp học).

Cung cấp các chức năng CRUD cho quản lý thông tin lớp học trong hệ thống điểm danh sinh trắc học.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional
from app.api import deps
from app.db.session import get_db
from app.models import ClassModel
from app.schemas import ClassBase

# Khởi tạo router cho class endpoints
router = APIRouter()

@router.get("/", response_model=list[ClassBase])
async def get_classes(skip: int = 0, limit: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    API endpoint lấy danh sách lớp học với phân trang offset/limit.

    Hỗ trợ phân trang bằng offset/limit để tối ưu hiệu suất.

    Args:
        skip: Số bản ghi bỏ qua (offset)
        limit: Số lượng bản ghi tối đa trả về
        db: Session database async

    Returns:
        List[ClassBase]: Danh sách các lớp học
    """
    query = select(ClassModel).order_by(ClassModel.class_id.asc()).offset(skip)
    if limit is not None:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{class_id}", response_model=ClassBase)
async def read_class(class_id: str, db: AsyncSession = Depends(get_db)):
    """
    API endpoint lấy thông tin chi tiết của một lớp học cụ thể.

    Args:
        class_id: ID duy nhất của lớp học
        db: Session database async

    Returns:
        ClassBase: Thông tin lớp học

    Raises:
        HTTPException: Nếu lớp không tồn tại (404)
    """
    result = await db.execute(select(ClassModel).where(ClassModel.class_id == class_id))
    class_obj = result.scalars().first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Lớp không tồn tại")
    return class_obj

@router.put("/{class_id}", response_model=ClassBase)
async def update_class(class_id: str, data: ClassBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """
    API endpoint cập nhật thông tin lớp học. Yêu cầu quyền admin.

    Args:
        class_id: ID của lớp cần cập nhật
        data: Dữ liệu cập nhật (ClassBase schema)
        db: Session database async
        _: Token xác thực admin (dependency injection)

    Returns:
        ClassBase: Thông tin lớp sau khi cập nhật

    Raises:
        HTTPException: Nếu lớp không tồn tại hoặc lỗi cập nhật
    """
    existing = await db.get(ClassModel, class_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Lớp không tồn tại")
    
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing, field, value)
    
    try:
        await db.commit()
        await db.refresh(existing)
        return existing
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi cập nhật: {str(e)}")

@router.post("/")
async def create_class(data: ClassBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """
    API endpoint tạo mới một lớp học. Yêu cầu quyền admin.

    Args:
        data: Dữ liệu lớp mới (ClassBase schema)
        db: Session database async
        _: Token xác thực admin

    Returns:
        ClassModel: Đối tượng lớp vừa tạo
    """
    obj = ClassModel(**data.dict())
    db.add(obj)
    await db.commit()
    return obj

@router.delete("/{id}")
async def delete_class(id: str, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """
    API endpoint xóa một lớp học theo ID. Yêu cầu quyền admin.

    Args:
        id: ID của lớp cần xóa
        db: Session database async
        _: Token xác thực admin

    Returns:
        dict: Thông báo xác nhận xóa

    Raises:
        HTTPException: Nếu lớp không tồn tại
    """
    existing = await db.get(ClassModel, id)
    if not existing:
        raise HTTPException(status_code=404, detail="Lớp không tồn tại")
    await db.delete(existing)
    await db.commit()
    return {"message": f"Đã xóa lớp {id}"}
