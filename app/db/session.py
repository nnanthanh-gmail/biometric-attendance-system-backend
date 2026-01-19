from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Động cơ bất đồng bộ với nhóm kết nối.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10
)

# Nhà máy phiên bất đồng bộ với expire_on_commit=False.
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Phụ thuộc cho vòng đời phiên bất đồng bộ.
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session