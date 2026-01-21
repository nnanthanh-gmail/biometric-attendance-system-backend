from pydantic import BaseModel

class FacultyBase(BaseModel):
    """
    Lược đồ cơ sở cho khoa với ID và tên.
    """
    faculty_id: str
    faculty_name: str

class FacultyCreate(FacultyBase):
    """
    Lược đồ tạo khoa.
    """
    pass

class FacultyResponse(FacultyBase):
    """
    Lược đồ phản hồi khoa.
    """
    class Config:
        from_attributes = True
