# Hệ Thống Điểm Danh Sinh Trắc Học - Hướng Dẫn API

## Tổng Quan

Hệ thống cung cấp REST API để quản lý và truy xuất dữ liệu điểm danh sinh trắc học. API sử dụng chuẩn RESTful với JSON responses.

## Cơ Sở Dữ Liệu

Hệ thống sử dụng PostgreSQL với các thực thể chính:
- Users: Thông tin người dùng cơ bản
- Accounts: Tài khoản xác thực
- Student/Lecturer Profiles: Hồ sơ chi tiết
- Fingerprints: Dữ liệu vân tay
- Classes, Subjects, Rooms: Cấu trúc đào tạo
- Attendance: Nhật ký điểm danh
- Course Registrations: Đăng ký khóa học

## Xác Thực

Một số endpoint yêu cầu xác thực:
- Basic Auth cho admin
- Bearer Token cho users
- API Key cho thiết bị phần cứng

## Phân Trang

Tất cả endpoint list sử dụng offset/limit pagination:
- `skip`: Số bản ghi bỏ qua (mặc định 0)
- `limit`: Số bản ghi tối đa trả về (tùy chọn)

## Endpoints Chính

### 1. Quản Lý Người Dùng

#### Lấy danh sách người dùng
```
GET /api/users/
```
Parameters: skip, limit

#### Lấy thông tin người dùng theo ID
```
GET /api/users/{user_id}
```

#### Tạo người dùng mới
```
POST /api/users/
```
Body: JSON với user_id, class_id, full_name

### 2. Quản Lý Tài Khoản

#### Lấy danh sách tài khoản
```
GET /api/accounts/
```
Parameters: skip, limit

#### Lấy thông tin tài khoản theo ID
```
GET /api/accounts/{user_id}
```

#### Lấy tài khoản theo vai trò
```
GET /api/accounts/role/{role}
```
Parameters: skip, limit

### 3. Hồ Sơ Sinh Viên

#### Lấy danh sách hồ sơ sinh viên
```
GET /api/profiles/student/
```
Parameters: skip, limit

#### Lấy hồ sơ sinh viên theo ID
```
GET /api/profiles/student/{user_id}
```

### 4. Hồ Sơ Giảng Viên

#### Lấy danh sách hồ sơ giảng viên
```
GET /api/profiles/lecturer/
```
Parameters: skip, limit

#### Lấy hồ sơ giảng viên theo ID
```
GET /api/profiles/lecturer/{user_id}
```

### 5. Vân Tay Sinh Trắc

#### Lấy danh sách vân tay theo người dùng
```
GET /api/fingerprints/user/{user_id}
```
Parameters: skip, limit

#### Lấy thông tin vân tay theo ID
```
GET /api/fingerprints/{finger_id}
```

### 6. Khoa

#### Lấy danh sách khoa
```
GET /api/faculties/
```
Parameters: skip, limit

#### Lấy thông tin khoa theo ID
```
GET /api/faculties/{faculty_id}
```

### 7. Chuyên Ngành

#### Lấy danh sách chuyên ngành theo khoa
```
GET /api/majors/faculty/{faculty_id}
```
Parameters: skip, limit

#### Lấy thông tin chuyên ngành theo ID
```
GET /api/majors/{major_id}
```

### 8. Cấp Độ Giáo Dục

#### Lấy danh sách cấp độ giáo dục
```
GET /api/education_levels/
```
Parameters: skip, limit

#### Lấy thông tin cấp độ theo ID
```
GET /api/education_levels/{level_id}
```

### 9. Lớp Học

#### Lấy danh sách lớp học
```
GET /api/classes/
```
Parameters: skip, limit

#### Lấy thông tin lớp học theo ID
```
GET /api/classes/{class_id}
```

### 10. Môn Học

#### Lấy danh sách môn học
```
GET /api/subjects/
```
Parameters: skip, limit

#### Lấy thông tin môn học theo ID
```
GET /api/subjects/{subject_id}
```

### 11. Phòng Học

#### Lấy danh sách phòng học
```
GET /api/rooms/
```
Parameters: skip, limit

#### Lấy thông tin phòng học theo ID
```
GET /api/rooms/{room_id}
```

### 12. Thời Khóa Biểu

#### Lấy danh sách thời khóa biểu
```
GET /api/schedules/
```
Parameters: skip, limit

#### Lấy thời khóa biểu theo ID
```
GET /api/schedules/{schedule_id}
```

### 13. Nhật Ký Điểm Danh

#### Lấy danh sách nhật ký điểm danh
```
GET /api/attendance/
```
Parameters: skip, limit

#### Lấy nhật ký theo ID
```
GET /api/attendance/{attendance_id}
```

### 14. Đăng Ký Khóa Học

#### Lấy danh sách đăng ký khóa học
```
GET /api/course_registrations/
```
Parameters: skip, limit

#### Lấy đăng ký theo ID
```
GET /api/course_registrations/{reg_id}
```

#### Lấy đăng ký theo người dùng
```
GET /api/course_registrations/user/{user_id}
```
Parameters: skip, limit

#### Lấy đăng ký theo môn học
```
GET /api/course_registrations/subject/{subject_id}
```
Parameters: skip, limit

#### Lấy đăng ký theo lớp học
```
GET /api/course_registrations/class/{class_id}
```
Parameters: skip, limit

### 15. Dashboard & Phân Tích

#### Lấy thống kê tổng quan cơ bản
```
GET /api/dashboard/stats
```
Trả về: total_users, total_students, total_lecturers, total_faculties, total_subjects, total_classes, total_rooms

#### Lấy lịch sử điểm danh của người dùng
```
GET /api/dashboard/attendance/user/{user_id}
```
Trả về danh sách bản ghi điểm danh với thông tin lớp, môn học, phòng học

#### Tìm kiếm lịch học
```
GET /api/dashboard/search?faculty_id=...&schedule_date=...&major_id=...&education_level_id=...
```
Parameters: faculty_id, schedule_date, major_id, education_level_id (tùy chọn)

#### Lấy báo cáo điểm danh theo ngày
```
GET /api/dashboard/attendance/{date}
```

### 16. Upload File

#### Upload ảnh profile
```
POST /api/upload/profile_image
```
Form data: file, user_id

#### Upload ảnh vân tay
```
POST /api/upload/fingerprint_image
```
Form data: file, finger_id

## Ví Dụ Sử Dụng

### Lấy danh sách sinh viên với phân trang
```bash
curl -X GET "http://localhost:8000/api/profiles/student/?skip=0&limit=10"
```

### Lấy thông tin sinh viên cụ thể
```bash
curl -X GET "http://localhost:8000/api/profiles/student/STU001"
```

### Lấy nhật ký điểm danh theo ngày
```bash
curl -X GET "http://localhost:8000/api/dashboard/attendance/2024-01-15"
```

## Response Format

Tất cả responses trả về JSON:
```json
{
  "data": [...],
  "total": 100,
  "skip": 0,
  "limit": 10
}
```

## Error Handling

- 200: Thành công
- 401: Chưa xác thực
- 403: Không có quyền
- 404: Không tìm thấy
- 400: Dữ liệu không hợp lệ

## Notes

- Sử dụng HTTPS trong production
- Rate limiting có thể áp dụng
- Logs được ghi tự động cho monitoring</content>