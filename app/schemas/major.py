from pydantic import BaseModel

class MajorBase(BaseModel):
    """
    Lược đồ cơ sở cho chuyên ngành với ID, khoa và tên.
    """
    major_id: str
    faculty_id: str
    major_name: str

class MajorCreate(MajorBase):
    """
    Lược đồ tạo chuyên ngành.
    """
    pass

class MajorResponse(MajorBase):
    """
    Lược đồ phản hồi chuyên ngành.
    """
    class Config:
        orm_mode = True
