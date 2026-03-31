import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api.router import api_router
from app.utils.exceptions import add_exception_handlers
from app.models import *
from fastapi.staticfiles import StaticFiles

if not os.path.exists("uploads"):
    os.makedirs("uploads")

Base.metadata.create_all(bind=engine)  # Enabled for Hard Reset

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

add_exception_handlers(app)

# ── Proxy Headers ─────────────────────────────────────────────────────────
# Crucial for running behind Azure App Service (or any SSL-terminating proxy)
# to ensure secure schemes (https) and IPs are correctly forwarded to FastAPI,
# preventing Mixed Content (HTTP 307 redirects) on trailing slash API routes.
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# ── Environment Detection ─────────────────────────────────────────────────
# Set ENVIRONMENT=production in the Azure App Service configuration panel.
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

# Force HTTPS scheme in production ASGI scope to avoid HTTP 307 redirects
# if Gunicorn/Azure strips X-Forwarded-Proto before it reaches Uvicorn.
class ForceHTTPSMiddleware:
    def __init__(self, app):
        self.app = app
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            if b"x-forwarded-proto" in headers:
                scope["scheme"] = headers[b"x-forwarded-proto"].decode("latin1").strip()
            elif IS_PRODUCTION:
                scope["scheme"] = "https"
        return await self.app(scope, receive, send)

app.add_middleware(ForceHTTPSMiddleware)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ── CORS — Production-Hardened ────────────────────────────────────────────
# Origins are driven by BACKEND_CORS_ORIGINS in .env (comma-separated).
# The explicit allow_headers list is critical: the wildcard "*" is rejected
# by browsers for credentialed requests (withCredentials: true / allow_credentials=True).
# ConsistencyLevel must be explicitly listed because it is a custom header
# sent by the frontend when proxying MS Graph advanced filter queries.
_raw_origins: list[str] = (
    [o.strip() for o in settings.BACKEND_CORS_ORIGINS]
    if settings.BACKEND_CORS_ORIGINS
    else ["https://wonderful-sea-0d2c3fd00.1.azurestaticapps.net"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_raw_origins,
    allow_credentials=True,                     # Required: pairs with withCredentials: true
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",                        # JWT Bearer token
        "Content-Type",                         # application/json
        "Accept",
        "Origin",
        "X-Requested-With",
        "ConsistencyLevel",                     # MS Graph: required for advanced $filter + $count
        "X-Forwarded-For",                      # Azure reverse-proxy headers
        "X-Forwarded-Proto",
    ],
    expose_headers=["Content-Disposition"],     # Enables file download filename parsing
    max_age=600,                                # Preflight cache: 10 minutes
)

# ── TrustedHost — Host Header Injection Prevention ────────────────────────
# Rejects requests with a Host header not in the allowlist.
# Prevents cache poisoning and SSRF via forged Host headers.
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "trucszohoreplica.azurewebsites.net",  # Azure App Service production
        "*.azurewebsites.net",                  # Allow staging slots (e.g. -staging)
        "localhost",                            # Local development
        "127.0.0.1",
    ],
)

# ── HTTPSRedirect — Production Only ──────────────────────────────────────
# Azure App Service terminates TLS at the load balancer and forwards requests
# internally over HTTP. HTTPSRedirectMiddleware inspects the raw scheme, which
# will always be "http" behind Azure's proxy — causing an infinite redirect loop
# if enabled unconditionally.
#
# Safe usage: only activate when ENVIRONMENT=production AND you have confirmed
# that Azure's "HTTPS Only" setting is ON (which handles the redirect at the
# Azure layer). If you rely on this middleware instead of Azure's setting,
# deploy behind a custom domain with a self-managed reverse proxy.
#
# To activate: set ENVIRONMENT=production in App Service → Configuration panel.
if IS_PRODUCTION:
    app.add_middleware(HTTPSRedirectMiddleware)

# ── Router Registration ───────────────────────────────────────────────────
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to TechnoRUCS PMS Backend API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
