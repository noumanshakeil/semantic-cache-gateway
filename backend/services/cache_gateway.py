from __future__ import annotations
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.llm import get_llm
from backend.models import CacheEntry, CacheQueryLog
from backend.utils.ids import short_id
from backend.utils.similarity import jaccard
from backend.utils.text import normalize

SIM_THRESHOLD = 0.72

async def list_entries(session: AsyncSession, limit: int = 50) -> list[CacheEntry]:
    stmt = select(CacheEntry).order_by(CacheEntry.created_at.desc()).limit(limit)
    return list((await session.execute(stmt)).scalars())

async def analytics(session: AsyncSession) -> dict:
    total = (await session.execute(select(func.count()).select_from(CacheQueryLog))).scalar() or 0
    hits = (
        await session.execute(select(func.count()).select_from(CacheQueryLog).where(CacheQueryLog.hit == 1))
    ).scalar() or 0
    return {
        "queries": int(total),
        "hits": int(hits),
        "misses": int(total) - int(hits),
        "hit_rate": (hits / total) if total else 0.0,
    }

async def _best_match(session: AsyncSession, prompt: str) -> tuple[CacheEntry | None, float]:
    entries = await list_entries(session, limit=200)
    best: CacheEntry | None = None
    best_score = 0.0
    for entry in entries:
        score = jaccard(prompt, entry.prompt_raw)
        if score > best_score:
            best_score = score
            best = entry
    return best, best_score

async def complete(session: AsyncSession, prompt: str, *, system: str | None = None) -> dict:
    norm = normalize(prompt)
    match, sim = await _best_match(session, prompt)
    if match and sim >= SIM_THRESHOLD:
        match.hits += 1
        session.add(
            CacheQueryLog(prompt=prompt[:4000], hit=1, similarity=sim, entry_id=match.id)
        )
        await session.commit()
        return {"cache": "hit", "similarity": round(sim, 3), "response": match.response, "entry_id": match.id}
    llm = get_llm()
    response = await llm.complete(prompt, system=system)
    entry = CacheEntry(
        id=short_id(),
        prompt_norm=norm,
        prompt_raw=prompt.strip(),
        response=response,
        hits=0,
    )
    session.add(entry)
    session.add(CacheQueryLog(prompt=prompt[:4000], hit=0, similarity=sim, entry_id=entry.id))
    await session.commit()
    return {"cache": "miss", "similarity": round(sim, 3), "response": response, "entry_id": entry.id}
