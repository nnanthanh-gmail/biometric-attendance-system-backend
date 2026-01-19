from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.api import deps
from app.db.session import get_db
from app.models import Account
from app.schemas import AccountBase, AccountCreate

router = APIRouter()

@router.get("/", response_model=list[AccountBase])
async def read_accounts(db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Lấy danh sách tài khoản."""
    result = await db.execute(select(Account))
    return result.scalars().all()

@router.post("/", response_model=AccountBase)
async def create_account(acc_in: AccountCreate, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Tạo tài khoản mới."""
    # Logic băm mật khẩu ở đây
    new_acc = Account(user_id=acc_in.user_id, role=acc_in.role, password_hash=acc_in.password) 
    db.add(new_acc)
    await db.commit()
    await db.refresh(new_acc)
    return new_acc

@router.delete("/{user_id}")
async def delete_account(user_id: str, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Xóa tài khoản theo ID người dùng."""
    await db.execute(delete(Account).where(Account.user_id == user_id))
    await db.commit()
    return {"status": "deleted"}
