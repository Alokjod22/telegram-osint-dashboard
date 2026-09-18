import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="OSINT Bot Admin Dashboard")

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    stats = {
        "active_investigations": 12,
        "total_searches": 148,
        "active_sources": 5,
        "reports_generated": 34
    }
    return templates.TemplateResponse(request=request, name="index.html", context={"stats": stats})

@app.get("/api/health")
async def health_check():
    return {"status": "HEALTHY", "service": "Telegram OSINT Research Engine"}
