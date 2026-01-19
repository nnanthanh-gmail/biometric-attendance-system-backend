from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.api import deps
from app.db.session import get_db
from app.models import StudentProfile
from app.schemas import StudentProfileBase

router = APIRouter()

@router.get("/{user_id}", response_model=StudentProfileBase)
async def get_profile(user_id: str, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Lấy hồ sơ sinh viên theo ID người dùng."""
    res = await db.get(StudentProfile, user_id)
    if not res: raise HTTPException(404, "Not Found")
    return res

@router.post("/")
async def create_profile(data: StudentProfileBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Tạo hồ sơ sinh viên mới."""
    obj = StudentProfile(**data.dict())
    db.add(obj)
    await db.commit()
    return obj
