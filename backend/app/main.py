from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.config import settings
from app.routers import health, trajets, stats

app = FastAPI(
    title="ObRail Europe API",
    description=(
        "API REST pour l'accès aux données ferroviaires européennes.\n\n"
        "Permet de consulter les trajets ferroviaires (trains de jour et de nuit), "
        "les statistiques de couverture, et de comparer les opérateurs européens.\n\n"
        "**Authentification** : tous les endpoints `/api/v1/` nécessitent l'header `X-API-Key`."
    ),
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ── OpenAPI : documentation sécurité ────────────────────────────────────────
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema["components"]["securitySchemes"] = {
        "ApiKeyHeader": {"type": "apiKey", "in": "header", "name": "X-API-Key"}
    }
    for path in schema["paths"].values():
        for method in path.values():
            method["security"] = [{"ApiKeyHeader": []}]
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi


# ── Middleware CORS ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(trajets.router, prefix="/api/v1/trajets", tags=["Trajets"])
app.include_router(stats.router,   prefix="/api/v1/stats",   tags=["Statistiques"])


# ── Endpoint racine ───────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
def root():
    return {
        "message":       "Bienvenue sur l'API ObRail Europe",
        "version":       settings.VERSION,
        "documentation": "/docs",
        "auth":          "Header X-API-Key requis sur /api/v1/*",
        "endpoints": {
            "trajets":       "/api/v1/trajets",
            "stats":         "/api/v1/stats/volumes",
            "jour_vs_nuit":  "/api/v1/stats/jour-vs-nuit",
            "par_operateur": "/api/v1/stats/par-operateur",
            "par_pays":      "/api/v1/stats/par-pays",
            "health":        "/health",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
