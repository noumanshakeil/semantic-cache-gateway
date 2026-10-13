from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import cache_gateway as svc

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Semantic Cache Gateway",
            "entries": await svc.list_entries(db),
            "analytics": await svc.analytics(db),
            "result": None,
        },
    )

@router.post("/ui/complete", response_class=HTMLResponse)
async def ui_complete(request: Request, prompt: str = Form(...), db: AsyncSession = Depends(get_db)):
    result = await svc.complete(db, prompt)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Semantic Cache Gateway",
            "entries": await svc.list_entries(db),
            "analytics": await svc.analytics(db),
            "result": result,
            "prompt": prompt,
        },
    )
