import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import select, desc

from database.session import AsyncSessionLocal, init_db
from database.models import BotUser, Investigation, SearchRecord, AbuseCase, AbuseEvidence
from database.user_manager import get_all_users, get_user_stats
from engine.research_manager import ResearchManager

app = FastAPI(title="OSINT Bot Enterprise Admin Portal")
research_manager = ResearchManager()

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    stats = await get_user_stats()
    users = await get_all_users(limit=25)
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"stats": stats, "users": users}
    )

@app.get("/api/health")
async def health_check():
    return {
        "status": "HEALTHY", 
        "service": "Telegram OSINT Research Engine & Telemetry Hub",
        "version": "2.4.0"
    }

@app.get("/api/stats")
async def api_stats():
    stats = await get_user_stats()
    return stats

@app.get("/api/users")
async def api_users(limit: int = 50):
    users = await get_all_users(limit=limit)
    return [
        {
            "id": u.id,
            "telegram_id": u.telegram_id,
            "username": u.username,
            "name": f"{u.first_name or ''} {u.last_name or ''}".strip() or "Anonymous User",
            "phone_number": u.phone_number,
            "is_verified": bool(u.is_verified),
            "query_count": u.query_count or 0,
            "report_count": u.report_count or 0,
            "first_seen": u.first_seen.strftime("%Y-%m-%d %H:%M") if u.first_seen else "N/A",
            "last_active": u.last_active.strftime("%Y-%m-%d %H:%M:%S") if u.last_active else "N/A"
        }
        for u in users
    ]

@app.get("/api/investigations")
async def api_investigations(limit: int = 20):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(SearchRecord).order_by(desc(SearchRecord.created_at)).limit(limit))
        records = res.scalars().all()
        return [
            {
                "id": r.id,
                "investigation_id": r.investigation_id,
                "search_type": r.search_type,
                "query": r.query,
                "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else "N/A"
            }
            for r in records
        ]

class SearchRequest(BaseModel):
    query: str
    search_type: str = "AUTO"

@app.post("/api/search")
async def api_run_search(payload: SearchRequest):
    if not payload.query:
        return JSONResponse({"error": "Empty query"}, status_code=400)
    result = await research_manager.execute_investigation(payload.query)
    return result

@app.get("/api/network-graph")
async def api_network_graph():
    # Return structured nodes & edges for graph visualization
    nodes = [
        {"id": "hub", "label": "OSINT Engine Hub", "group": "server", "shape": "dot", "size": 25},
        {"id": "tg_bot", "label": "Telegram Bot", "group": "bot", "shape": "diamond", "size": 20}
    ]
    edges = [
        {"from": "tg_bot", "to": "hub"}
    ]

    users = await get_all_users(limit=15)
    for u in users:
        u_label = f"@{u.username}" if u.username else f"User {u.telegram_id}"
        nodes.append({
            "id": f"user_{u.telegram_id}", 
            "label": u_label, 
            "group": "verified" if u.is_verified else "user",
            "title": f"Phone: {u.phone_number or 'Not Linked'}"
        })
        edges.append({"from": f"user_{u.telegram_id}", "to": "tg_bot"})

    return {"nodes": nodes, "edges": edges}
