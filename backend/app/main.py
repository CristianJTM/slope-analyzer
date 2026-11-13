from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.routes import router
from .db.database import engine
from .db.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="slope-analyzer", version="0.3.0", lifespan=lifespan)
app.include_router(router, prefix="/api/v1")
