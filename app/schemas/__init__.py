"""
Lược đồ Pydantic cho xác thực yêu cầu/phản hồi API.
"""
from .user import UserBase, UserCreate, UserResponse, UserUpdate
from .account import AccountBase, AccountCreate, AccountResponse, LoginRequest, TokenResponse
from .student_profile import StudentProfileBase, StudentProfileCreate, StudentProfileResponse
from .lecturer_profile import LecturerProfileBase, LecturerProfileCreate, LecturerProfileResponse
from .fingerprint import FingerprintBase, FingerprintCreate, FingerprintResponse
from .faculty import FacultyBase, FacultyCreate, FacultyResponse
from .major import MajorBase, MajorCreate, MajorResponse
from .education_level import EducationLevelBase, EducationLevelResponse
from .class_schema import ClassBase, ClassCreate, ClassResponse
from .subject import SubjectBase, SubjectCreate, SubjectResponse
from .room import RoomBase, RoomCreate, RoomResponse
from .schedule import ScheduleBase, ScheduleCreate, ScheduleResponse
from .course_registration import CourseRegBase, CourseRegCreate, CourseRegResponse
from .attendance import AttendanceBase, AttendanceCreate, AttendanceResponse
