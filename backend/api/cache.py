from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import cache_gateway as svc

class CompleteIn(BaseModel):
    prompt: str = Field(min_length=2)
    system: str | None = None

router = APIRouter()

@router.get("/entries")
async def entries(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_entries(db)
    return {
        "entries": [
            {"id": e.id, "prompt": e.prompt_raw[:160], "hits": e.hits, "response": e.response[:160]}
            for e in rows
        ]
    }

@router.get("/analytics")
async def analytics(db: AsyncSession = Depends(get_db)):
    return await svc.analytics(db)

@router.post("/complete")
async def complete(payload: CompleteIn, db: AsyncSession = Depends(get_db)):
    return await svc.complete(db, payload.prompt, system=payload.system)
