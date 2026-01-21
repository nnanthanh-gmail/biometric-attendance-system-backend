from pydantic import BaseModel

class RoomBase(BaseModel):
    """
    Lược đồ cơ sở cho phòng với ID và tên.
    """
    room_id: str
    room_name: str

class RoomCreate(RoomBase):
    """
    Lược đồ tạo phòng.
    """
    pass

class RoomResponse(RoomBase):
    """
    Lược đồ phản hồi phòng.
    """
    class Config:
        from_attributes = True
