from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Tối ưu Connection Pooling cho RAM 1GB
# pool_size=5: Giữ 5 kết nối thường trực
# max_overflow=10: Cho phép tối đa 10 kết nối tràn khi cao điểm
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency Injection cho FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session