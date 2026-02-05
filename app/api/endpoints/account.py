"""
Endpoints quản lý tài khoản.

Cung cấp CRUD operations cho user accounts, authentication và profile access.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional
from app.api import deps
from app.db.session import get_db
from app.models import Account, User
from app.schemas import AccountBase, AccountCreate, LoginRequest, TokenResponse, UserResponse

router = APIRouter()

@router.get("/", response_model=list[AccountBase])
async def read_accounts(skip: int = 0, limit: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    Lấy danh sách tất cả accounts với pagination.

    Args:
        skip: Số records bỏ qua
        limit: Số records tối đa trả về
        db: Database session

    Returns:
        List các account objects
    """
    query = select(Account).order_by(Account.user_id.asc()).offset(skip)
    if limit is not None:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{user_id}", response_model=AccountBase)
async def read_account(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Lấy thông tin account cụ thể theo user ID.

    Args:
        user_id: ID duy nhất của user
        db: Database session

    Returns:
        Account object

    Raises:
        HTTPException: Nếu account không tồn tại
    """
    result = await db.execute(select(Account).where(Account.user_id == user_id))
    account = result.scalars().first()
    if not account:
        raise HTTPException(status_code=404, detail="Account không tồn tại")
    return account

@router.get("/role/{role}", response_model=list[AccountBase])
async def read_accounts_by_role(role: str, skip: int = 0, limit: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    API endpoint lấy danh sách tài khoản theo vai trò với phân trang offset/limit.

    Hỗ trợ phân trang bằng offset/limit để tối ưu hiệu suất.

    Args:
        role: Vai trò người dùng để lọc
        skip: Số bản ghi bỏ qua (offset)
        limit: Số lượng bản ghi tối đa trả về
        db: Session database async

    Returns:
        List[AccountBase]: Danh sách tài khoản theo vai trò
    """
    query = select(Account).where(Account.role == role).order_by(Account.user_id.asc()).offset(skip)
    if limit:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=AccountBase)
async def create_account(acc_in: AccountCreate, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """
    Tạo account mới. Yêu cầu admin authentication.

    Args:
        acc_in: Dữ liệu tạo account
        db: Database session
        _: Admin authentication dependency

    Returns:
        Account object đã tạo

    Raises:
        HTTPException: Nếu user không tồn tại hoặc account đã có
    """
    # Check user tồn tại
    user_result = await db.execute(select(User).where(User.user_id == acc_in.user_id))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=400,
            detail=f"User với ID '{acc_in.user_id}' không tồn tại. Tạo user trước."
        )

    # Check account đã tồn tại
    account_result = await db.execute(select(Account).where(Account.user_id == acc_in.user_id))
    existing_account = account_result.scalars().first()
    if existing_account:
        raise HTTPException(
            status_code=400,
            detail=f"Account cho user '{acc_in.user_id}' đã tồn tại."
        )

    # Hash password
    hashed_password = deps.hash_password(acc_in.password)
    new_acc = Account(user_id=acc_in.user_id, role=acc_in.role, password_hash=hashed_password)
    db.add(new_acc)
    try:
        await db.commit()
        return AccountBase(user_id=new_acc.user_id, role=new_acc.role)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Tạo account thất bại: {str(e)}")

@router.put("/{user_id}", response_model=AccountBase)
async def update_account(user_id: str, acc_in: AccountCreate, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """
    Cập nhật account hiện có. Yêu cầu admin authentication.

    Args:
        user_id: User ID hiện tại
        acc_in: Dữ liệu account cập nhật
        db: Database session
        _: Admin authentication dependency

    Returns:
        Account object đã cập nhật

    Raises:
        HTTPException: Nếu account không tồn tại hoặc validation thất bại
    """
    # Check account tồn tại
    existing_account = await db.get(Account, user_id)
    if not existing_account:
        raise HTTPException(status_code=404, detail="Account không tồn tại")

    update_data = acc_in.dict(exclude_unset=True)

    # Handle user_id change
    if 'user_id' in update_data and update_data['user_id'] != user_id:
        new_user_id = update_data['user_id']
        # Verify new user tồn tại
        user_result = await db.execute(select(User).where(User.user_id == new_user_id))
        user = user_result.scalars().first()
        if not user:
            raise HTTPException(status_code=400, detail=f"User '{new_user_id}' không tồn tại")
        # Check new account không tồn tại
        account_result = await db.execute(select(Account).where(Account.user_id == new_user_id))
        if account_result.scalars().first():
            raise HTTPException(status_code=400, detail=f"Account cho '{new_user_id}' đã tồn tại")

        # Cập nhật
        existing_account.user_id = new_user_id
        # Cập nhật password nếu có
        if 'password' in update_data:
            existing_account.password_hash = deps.hash_password(update_data['password'])
        if 'role' in update_data:
            existing_account.role = update_data['role']
    else:
        # Cập nhật bình thường
        if 'password' in update_data:
            existing_account.password_hash = deps.hash_password(update_data['password'])
        if 'role' in update_data:
            existing_account.role = update_data['role']

    try:
        await db.commit()
        await db.refresh(existing_account)
        return AccountBase(user_id=existing_account.user_id, role=existing_account.role)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Cập nhật thất bại: {str(e)}")

@router.delete("/{user_id}")
async def delete_account(user_id: str, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """
    Xóa account theo user ID. Yêu cầu admin authentication.

    Args:
        user_id: User ID cần xóa
        db: Database session
        _: Admin authentication dependency

    Returns:
        Thông báo thành công

    Raises:
        HTTPException: Nếu account không tồn tại
    """
    existing = await db.get(Account, user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Account không tồn tại")
    await db.delete(existing)
    await db.commit()
    return {"message": f"Account {user_id} đã xóa thành công"}

@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Xác thực user và trả về JWT access token.

    Args:
        login_data: Credentials đăng nhập
        db: Database session

    Returns:
        JWT token response

    Raises:
        HTTPException: Nếu credentials không hợp lệ
    """
    # Tìm account
    result = await db.execute(select(Account).where(Account.user_id == login_data.user_id))
    account = result.scalars().first()

    if not account or not deps.verify_password(login_data.password, account.password_hash):
        raise HTTPException(
            status_code=401,
            detail="User ID hoặc password không chính xác"
        )

    # Tạo access token
    access_token = deps.create_access_token(data={"sub": account.user_id, "role": account.role})

    return TokenResponse(access_token=access_token, user_id=account.user_id, role=account.role)
