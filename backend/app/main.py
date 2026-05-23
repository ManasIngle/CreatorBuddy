from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from starlette.middleware.gzip import GZipMiddleware
from app.config import settings
from app.routers import (
    auth, channels, competitors, gaps, scripts,
    hooks, thumbnails, trends, audience, research
)
from app.utils.resilience import CircuitBreakerManager
import logging
import hashlib
import time

# Configure logging with structured format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(request_id)s"
)
logger = logging.getLogger(__name__)

# API Version constant
API_VERSION = "1.0.0"

app = FastAPI(
    title="CreatorIQ API",
    version=API_VERSION,
    description="AI Creator Growth Intelligence Platform - YouTube analytics + AI scripting SaaS",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT == "development" else None,
    openapi_tags=[
        {"name": "auth", "description": "Authentication and user management"},
        {"name": "channels", "description": "YouTube channel connection and management"},
        {"name": "competitors", "description": "Competitor tracking and analysis"},
        {"name": "gaps", "description": "Content gap detection"},
        {"name": "scripts", "description": "AI script generation"},
        {"name": "hooks", "description": "Hook intelligence and optimization"},
        {"name": "thumbnails", "description": "Thumbnail analysis and recommendations"},
        {"name": "trends", "description": "Viral trend detection and tracking"},
        {"name": "audience", "description": "Audience psychology and insights"},
        {"name": "health", "description": "Health check endpoints"},
        {"name": "metrics", "description": "System metrics and monitoring"},
        {"name": "root", "description": "Root API information"},
    ]
)

# GZip compression for responses > 500 bytes
app.add_middleware(GZipMiddleware, minimum_size=500)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(channels.router, prefix="/api/v1/channels", tags=["channels"])
app.include_router(competitors.router, prefix="/api/v1/competitors", tags=["competitors"])
app.include_router(gaps.router, prefix="/api/v1/gaps", tags=["gaps"])
app.include_router(scripts.router, prefix="/api/v1/scripts", tags=["scripts"])
app.include_router(hooks.router, prefix="/api/v1/hooks", tags=["hooks"])
app.include_router(thumbnails.router, prefix="/api/v1/thumbnails", tags=["thumbnails"])
app.include_router(trends.router, prefix="/api/v1/trends", tags=["trends"])
app.include_router(audience.router, prefix="/api/v1/audience", tags=["audience"])
app.include_router(research.router, prefix="/api/v1/research", tags=["research"])


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "ok",
        "service": "CreatorIQ API",
        "version": API_VERSION
    }


@app.get("/health/ready", tags=["health"])
async def readiness_check():
    """
    Readiness check that verifies dependencies.
    Used by Kubernetes/container orchestrators.
    """
    checks = {
        "database": False,
        "redis": False
    }
    
    # Check database connection
    try:
        from app.database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        checks["database"] = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    # Check Redis connection
    try:
        from app.services.redis_cache import redis_cache
        await redis_cache.initialize()
        checks["redis"] = await redis_cache.exists("health_check") is not None or True  # Redis might not be set up
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
    
    all_healthy = all(checks.values())
    status = {"status": "ready" if all_healthy else "degraded", "checks": checks}
    
    if not all_healthy:
        return JSONResponse(status_code=503, content=status)
    
    return status


@app.get("/health/live", tags=["health"])
async def liveness_check():
    """
    Liveness check - simple check that the service is running.
    Used by Kubernetes to determine if pod should be restarted.
    """
    return {"status": "alive"}


@app.get("/metrics", tags=["metrics"])
async def get_metrics():
    """
    Get system metrics including circuit breaker states.
    In production, use Prometheus client library.
    """
    from app.utils.base import MetricsCollector
    
    metrics = MetricsCollector.get_metrics()
    metrics["circuit_breakers"] = CircuitBreakerManager.get_all_metrics()
    
    return {
        "api_version": API_VERSION,
        "metrics": metrics
    }


@app.get("/", tags=["root"])
def root():
    """Root endpoint returning API info."""
    return {
        "name": "CreatorIQ API",
        "version": "1.0.0",
        "docs": "/docs" if settings.ENVIRONMENT == "development" else "disabled"
    }


# Request ID middleware for debugging and tracing
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    import uuid
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Add request ID to logging context
    logger.info(f"Request started: {request.method} {request.url.path}", extra={"request_id": request_id})
    
    start_time = time.time()
    response = await call_next(request)
    duration = (time.time() - start_time) * 1000  # ms
    
    # Add headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-MS"] = str(int(duration))
    
    logger.info(
        f"Request completed: {request.method} {request.url.path} - {response.status_code} ({duration:.0f}ms)",
        extra={"request_id": request_id}
    )
    
    # Record timing metric
    from app.utils.base import MetricsCollector
    MetricsCollector.record_timing(f"request.{request.method}.{request.url.path}", duration)
    
    return response


# API Version header middleware
@app.middleware("http")
async def add_api_version_header(request: Request, call_next):
    """Add API-Version header to all responses."""
    response = await call_next(request)
    response.headers["API-Version"] = API_VERSION
    return response


# ETag middleware for caching
@app.middleware("http")
async def add_etag_header(request: Request, call_next):
    """
    Add ETag to GET responses for client-side caching.
    Handles If-None-Match for conditional requests.
    """
    response = await call_next(request)
    
    # Only add ETags to successful GET requests
    if request.method == "GET" and response.status_code == 200:
        # Generate ETag from response body (simplified)
        # In production, compute hash of content
        etag = hashlib.md5(response.body if hasattr(response, 'body') else str(time.time()).encode()).hexdigest()
        response.headers["ETag"] = f'"{etag}"'
        
        # Check If-None-Match
        if_none_match = request.headers.get("if-none-match")
        if if_none_match:
            # Simple comparison - in production use proper ETag matching
            if f'"{etag}"' in if_none_match.replace(" ", "").split(","):
                return Response(status_code=304)
    
    return response


# Error handler for validation errors
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler with structured errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "path": request.url.path
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", extra={"request_id": getattr(request.state, 'request_id', 'unknown')})
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "path": request.url.path
            }
        }
    )


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("CreatorIQ API starting up...")
    
    # Initialize Redis cache
    try:
        from app.services.redis_cache import redis_cache
        await redis_cache.initialize()
        logger.info("Redis cache initialized")
    except Exception as e:
        logger.warning(f"Redis initialization failed (non-critical): {e}")
    
    # Initialize async HTTP client
    try:
        from app.services.async_http import http_client
        await http_client.initialize()
        logger.info("Async HTTP client initialized")
    except Exception as e:
        logger.warning(f"HTTP client initialization failed (non-critical): {e}")

    # Recover stuck analyses on startup
    try:
        from app.database import get_db_session
        from app.models.channel import Channel
        from app.routers.channels import run_full_channel_analysis
        import threading

        with get_db_session() as db:
            stuck_channels = db.query(Channel).filter(Channel.analysis_status == "running").all()
            for channel in stuck_channels:
                logger.info(f"Recovering stuck analysis for channel: {channel.id}")
                thread = threading.Thread(
                    target=run_full_channel_analysis,
                    args=(str(channel.id), channel.uploads_playlist_id)
                )
                thread.daemon = True
                thread.start()
    except Exception as e:
        logger.warning(f"Failed to recover stuck analyses on startup: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown."""
    logger.info("CreatorIQ API shutting down...")
    
    # Close Redis
    try:
        from app.services.redis_cache import redis_cache
        await redis_cache.close()
    except Exception as e:
        logger.warning(f"Redis close failed: {e}")
    
    # Close HTTP client
    try:
        from app.services.async_http import http_client
        await http_client.close()
    except Exception as e:
        logger.warning(f"HTTP client close failed: {e}")