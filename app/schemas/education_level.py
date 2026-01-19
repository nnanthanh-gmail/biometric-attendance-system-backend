from pydantic import BaseModel

class EducationLevelBase(BaseModel):
    """
    Lược đồ cơ sở cho cấp độ giáo dục với ID và tên.
    """
    edu_level_id: str
    edu_level_name: str

class EducationLevelResponse(EducationLevelBase):
    """
    Lược đồ phản hồi cấp độ giáo dục.
    """
    class Config:
        orm_mode = True
