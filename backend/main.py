"""
MI Batting Prediction — FastAPI Backend
=========================================
Run: uvicorn main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, predict, stats, history

app = FastAPI(
    title="MI Batting Prediction API",
    description="Predictive analytics for Mumbai Indians batting performance (IPL)",
    version="1.0.0",
)

# ── CORS (allow Next.js frontend) ─────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────
app.include_router(auth.router,    prefix="/api/auth",    tags=["Auth"])
app.include_router(predict.router, prefix="/api/predict", tags=["Prediction"])
app.include_router(stats.router,   prefix="/api/stats",   tags=["Stats"])
app.include_router(history.router, prefix="/api/history", tags=["History"])


@app.get("/")
def root():
    return {
        "success": True,
        "message": "MI Batting Prediction API is running",
        "docs": "/docs",
    }
