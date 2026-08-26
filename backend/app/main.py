from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.tally import router as tally_router
from app.api.dashboard import router as dashboard_router
from app.api.reports import router as reports_router

app = FastAPI(
    title="Tally Financial Intelligence API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost:\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    tally_router,
    prefix="/api/v1/tally",
    tags=["Tally"]
)

app.include_router(
    dashboard_router,
    prefix="/api/v1/dashboard",
    tags=["Dashboard"]
)

app.include_router(
    reports_router,
    prefix="/api/v1/reports",
    tags=["Reports"]
)


@app.get("/")
def root():
    return {
        "message": "Tally Financial Intelligence API is running"
    }