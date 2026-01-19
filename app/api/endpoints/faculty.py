from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.api import deps
from app.db.session import get_db
from app.models import Faculty
from app.schemas import FacultyBase

router = APIRouter()

@router.get("/", response_model=list[FacultyBase])
async def list_faculty(db: AsyncSession = Depends(get_db)):
    """Lấy danh sách khoa."""
    res = await db.execute(select(Faculty))
    return res.scalars().all()

@router.post("/")
async def create_faculty(data: FacultyBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Tạo khoa mới."""
    obj = Faculty(**data.dict())
    db.add(obj)
    await db.commit()
    return obj

@router.delete("/{id}")
async def remove_faculty(id: str, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Xóa khoa theo ID."""
    await db.execute(delete(Faculty).where(Faculty.faculty_id == id))
    await db.commit()
    return {"msg": "Deleted"}
