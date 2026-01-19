from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.api import deps
from app.db.session import get_db
from app.models import ClassModel
from app.schemas import ClassBase

router = APIRouter()

@router.get("/", response_model=list[ClassBase])
async def get_classes(db: AsyncSession = Depends(get_db)):
    """Lấy danh sách lớp."""
    res = await db.execute(select(ClassModel))
    return res.scalars().all()

@router.post("/")
async def create_class(data: ClassBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Tạo lớp mới."""
    obj = ClassModel(**data.dict())
    db.add(obj)
    await db.commit()
    return obj

@router.delete("/{id}")
async def delete_class(id: str, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Xóa lớp theo ID."""
    await db.execute(delete(ClassModel).where(ClassModel.class_id == id))
    await db.commit()
    return {"msg": "Deleted"}
