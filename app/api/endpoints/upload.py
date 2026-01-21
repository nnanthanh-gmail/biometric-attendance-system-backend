from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
import shutil
from pathlib import Path
from app.api import deps
from app.db.session import get_db
from app.models.student_profile import StudentProfile
from app.models.lecturer_profile import LecturerProfile

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Tạo thư mục con cho các loại file khác nhau
PROFILE_IMAGES_DIR = UPLOAD_DIR / "profile_images"
FINGERPRINT_IMAGES_DIR = UPLOAD_DIR / "fingerprint_images"
PROFILE_IMAGES_DIR.mkdir(exist_ok=True)
FINGERPRINT_IMAGES_DIR.mkdir(exist_ok=True)

@router.post("/student_profile_image/{student_id}")
async def upload_student_profile_image(
    student_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(deps.verify_admin_auth)
):
    """Upload ảnh đại diện cho sinh viên."""
    # Kiểm tra sinh viên có tồn tại không
    result = await db.execute(select(StudentProfile).where(StudentProfile.user_id == student_id))
    student_profile = result.scalar_one_or_none()
    
    if not student_profile:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ sinh viên")

    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file ảnh")

    # Validate file size (max 5MB)
    content = await file.read()
    file_size = len(content)

    if file_size > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(status_code=400, detail="File quá lớn (tối đa 5MB)")

    # Generate filename
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in [".jpg", ".jpeg", ".png", ".gif"]:
        raise HTTPException(status_code=400, detail="Định dạng file không hỗ trợ")

    filename = f"{student_id}_profile{file_extension}"
    file_path = PROFILE_IMAGES_DIR / filename

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lưu file: {str(e)}")

    # Update profile_image_url in database
    file_url = f"/uploads/profile_images/{filename}"
    student_profile.profile_image_url = file_url
    await db.commit()

    return {
        "filename": filename,
        "url": file_url,
        "size": file_size,
        "message": "Upload ảnh đại diện sinh viên thành công"
    }

@router.post("/lecturer_profile_image/{lecturer_id}")
async def upload_lecturer_profile_image(
    lecturer_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(deps.verify_admin_auth)
):
    """Upload ảnh đại diện cho giảng viên."""
    # Kiểm tra giảng viên có tồn tại không
    result = await db.execute(select(LecturerProfile).where(LecturerProfile.user_id == lecturer_id))
    lecturer_profile = result.scalar_one_or_none()
    
    if not lecturer_profile:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ giảng viên")

    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file ảnh")

    # Validate file size (max 5MB)
    content = await file.read()
    file_size = len(content)

    if file_size > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(status_code=400, detail="File quá lớn (tối đa 5MB)")

    # Generate filename
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in [".jpg", ".jpeg", ".png", ".gif"]:
        raise HTTPException(status_code=400, detail="Định dạng file không hỗ trợ")

    filename = f"{lecturer_id}_profile{file_extension}"
    file_path = PROFILE_IMAGES_DIR / filename

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lưu file: {str(e)}")

    # Update profile_image_url in database
    file_url = f"/uploads/profile_images/{filename}"
    lecturer_profile.profile_image_url = file_url
    await db.commit()

    return {
        "filename": filename,
        "url": file_url,
        "size": file_size,
        "message": "Upload ảnh đại diện giảng viên thành công"
    }

@router.delete("/files/{file_path:path}")
async def delete_uploaded_file(
    file_path: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(deps.verify_admin_auth)
):
    """Xóa file đã upload."""
    # Security check - chỉ cho phép xóa trong thư mục uploads
    if not file_path.startswith("uploads/"):
        raise HTTPException(status_code=400, detail="Đường dẫn không hợp lệ")

    full_path = Path(file_path)
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File không tồn tại")

    try:
        os.remove(full_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xóa file: {str(e)}")

    return {"message": "Đã xóa file thành công"}