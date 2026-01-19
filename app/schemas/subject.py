from pydantic import BaseModel

class SubjectBase(BaseModel):
    """
    Lược đồ cơ sở cho môn học với ID, tên, tín chỉ, lý thuyết, thực hành và học kỳ.
    """
    subject_id: str
    subject_name: str
    credits: int
    theory: int
    practice: int
    semester: int

class SubjectCreate(SubjectBase):
    """
    Lược đồ tạo môn học.
    """
    pass

class SubjectResponse(SubjectBase):
    """
    Lược đồ phản hồi môn học.
    """
    class Config:
        orm_mode = True
