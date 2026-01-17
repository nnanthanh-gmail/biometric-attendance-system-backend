import uvicorn
from fastapi import FastAPI, Depends
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from app.api import deps
from app.api.endpoints import users, device

# -----------------------------------------------------------------------------
# KHỞI TẠO ỨNG DỤNG
# -----------------------------------------------------------------------------
app = FastAPI(
    title="Attendance System API",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# -----------------------------------------------------------------------------
# ĐĂNG KÝ ROUTER
# -----------------------------------------------------------------------------
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(device.router, prefix="/api/device", tags=["Device"])

# -----------------------------------------------------------------------------
# CẤU HÌNH TÀI LIỆU (NATIVE OPENAPI CONFIGURATION)
# -----------------------------------------------------------------------------

@app.get("/docs", include_in_schema=False)
async def get_swagger_documentation(username: str = Depends(deps.verify_admin_auth)):
    """
    Render giao diện Swagger UI sử dụng cấu hình Native.
    
    Lưu ý kỹ thuật:
        - Không sử dụng CSS Injection tùy chỉnh.
        - Sử dụng 'tryItOutEnabled': True để luôn mở form nhập liệu.
        - Hệ quả: Nút 'Cancel' sẽ vẫn hiển thị theo mặc định của thư viện Swagger UI.
    """
    return get_swagger_ui_html(
        openapi_url="/openapi.json", 
        title="Attendance API Docs",
        swagger_ui_parameters={
            "tryItOutEnabled": True,        # Tự động mở chế độ Execute
            "defaultModelsExpandDepth": -1, # Ẩn phần Models ở cuối trang cho gọn
            "displayRequestDuration": True  # Hiển thị thời gian phản hồi
        }
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint(username: str = Depends(deps.verify_admin_auth)):
    """
    Tạo và làm sạch cấu trúc OpenAPI (Schema Sanitization).
    """
    if app.openapi_schema:
        return app.openapi_schema
        
    # 1. Sinh Schema gốc
    openapi_schema = get_openapi(
        title="Attendance System API",
        version="1.0.0",
        routes=app.routes,
    )
    
    # 2. Xóa cấu hình Security Global
    if "components" in openapi_schema and "securitySchemes" in openapi_schema["components"]:
        del openapi_schema["components"]["securitySchemes"]
    
    if "security" in openapi_schema:
        del openapi_schema["security"]

    # 3. Duyệt và làm sạch từng Endpoint
    paths = openapi_schema.get("paths", {})
    params_to_hide = ["x-api-key", "api-key", "apikey"]

    for path, methods in paths.items():
        for method, operation in methods.items():
            
            # Xóa Security Requirements
            if "security" in operation:
                del operation["security"]
            
            # Lọc bỏ Parameter bị cấm
            if "parameters" in operation:
                operation["parameters"] = [
                    param for param in operation["parameters"] 
                    if param.get("name").lower() not in params_to_hide
                ]

    app.openapi_schema = openapi_schema
    return JSONResponse(app.openapi_schema)

# -----------------------------------------------------------------------------
# ENTRY POINT
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )