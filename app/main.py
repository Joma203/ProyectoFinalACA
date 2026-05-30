import os

from fastapi import FastAPI  # type: ignore[reportMissingImports]

from app.routes.reports import router as reports_router

app = FastAPI(
    title=os.getenv("APP_NAME", "OpenVAS Analyzer API"),
    version=os.getenv("APP_VERSION", "1.0.0"),
)

app.include_router(reports_router)


@app.get("/health", tags=["Health"])
def health_check():
    """
    Endpoint de health check para Docker / orquestadores.
    Devuelve 200 si la aplicación está viva.
    """
    return {
        "status": "ok",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": os.getenv("APP_VERSION", "1.0.0"),
    }
