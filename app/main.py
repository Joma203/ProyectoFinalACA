from fastapi import FastAPI  # type: ignore[reportMissingImports]
from app.routes.reports import router as reports_router

app = FastAPI(
    title="OpenVAS Analyzer API",
    version="1.0.0"
)

app.include_router(reports_router)
