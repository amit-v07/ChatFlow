from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.services.redis_service import redis_service
from app.api import auth
from app.websocket import ws_endpoint, chat_ws, call_ws


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    await redis_service.connect()
    print(f"✓ Redis connected: {settings.REDIS_URL}")
    print(f"✓ Database URL: {settings.DATABASE_URL}")
    
    yield
    
    # Shutdown
    await redis_service.disconnect()
    print("✓ Redis disconnected")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(ws_endpoint.router)  # WebSocket routes
app.include_router(chat_ws.router)  # Chat WebSocket routes
app.include_router(call_ws.router)  # Call signaling WebSocket routes
from app.api import friends, chat
app.include_router(friends.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
