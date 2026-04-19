import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient, ASGITransport

from src.models.model import Base
from src.main import app
from src.dependincies import get_db, verify_user


TEST_ENGINE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def override_db():
    test_engine = create_async_engine(url=TEST_ENGINE_URL)
    test_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        
    async def mock_get_db():
        async with test_session() as db:    
            yield db
            
            await db.close()
        
    app.dependency_overrides[get_db] = mock_get_db
    
    yield
    
    app.dependency_overrides.clear()
        
        
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()
        
        
@pytest_asyncio.fixture
async def client(override_db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
        
        

@pytest.fixture
def jwt_user_id():
    def mock_verify_user():
        return 123
    
    app.dependency_overrides[verify_user] = mock_verify_user
    
    yield
    
    app.dependency_overrides.clear()
