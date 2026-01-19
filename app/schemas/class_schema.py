from pydantic import BaseModel

class ClassBase(BaseModel):
    """
    Lược đồ cơ sở cho lớp với ID, chuyên ngành, cấp độ, tên, khóa học và năm.
    """
    class_id: str
    major_id: str
    edu_level_id: str
    class_name: str
    course: str
    enroll_year: int

class ClassCreate(ClassBase):
    """
    Lược đồ tạo lớp.
    """
    pass

class ClassResponse(ClassBase):
    """
    Lược đồ phản hồi lớp.
    """
    class Config:
        orm_mode = True
