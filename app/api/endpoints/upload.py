from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
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

@router.get("/profile_images/{filename}")
async def get_profile_image(filename: str):
    """Lấy ảnh đại diện từ thư mục profile_images."""
    file_path = PROFILE_IMAGES_DIR / filename
    
    # Security check - chỉ cho phép lấy file trong thư mục profile_images
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Ảnh không tồn tại")
    
    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="Đường dẫn không hợp lệ")
    
    return FileResponse(path=file_path, media_type="image/jpeg")

@router.get("/fingerprint_images/{filename}")
async def get_fingerprint_image(filename: str):
    """Lấy ảnh vân tay từ thư mục fingerprint_images."""
    file_path = FINGERPRINT_IMAGES_DIR / filename
    
    # Security check - chỉ cho phép lấy file trong thư mục fingerprint_images
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Ảnh không tồn tại")
    
    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="Đường dẫn không hợp lệ")
    
    return FileResponse(path=file_path, media_type="image/jpeg")

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
    student_profile.profile_image_url = filename
    await db.commit()

    return {
        "filename": filename,
        "url": filename,
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
    lecturer_profile.profile_image_url = filename
    await db.commit()

    return {
        "filename": filename,
        "url": filename,
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