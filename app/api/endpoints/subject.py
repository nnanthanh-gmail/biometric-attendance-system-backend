from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.api import deps
from app.db.session import get_db
from app.models import Subject
from app.schemas import SubjectBase

router = APIRouter()

@router.get("/", response_model=list[SubjectBase])
async def list_subjects(db: AsyncSession = Depends(get_db)):
    """Lấy danh sách môn học."""
    res = await db.execute(select(Subject))
    return res.scalars().all()

@router.post("/")
async def create_subject(data: SubjectBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Tạo môn học mới."""
    obj = Subject(**data.dict())
    db.add(obj)
    await db.commit()
    return obj
