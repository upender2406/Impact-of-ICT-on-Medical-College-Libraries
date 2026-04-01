from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from app.routes import data, predictions, analysis, reports, admin, auth, approvals, notifications
from app.utils.init_database import initialize_database

load_dotenv()

app = FastAPI(
    title="ICT Impact Assessment API",
    description="AI-powered API for medical college library ICT impact assessment",
    version="2.0.0",
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    print("Starting application...")
    initialize_database()
    print("Application started successfully!")

# CORS configuration
# Default to common local dev origins (Vite default + 127.0.0.1). Can be overridden with CORS_ORIGINS env var
default_origins = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"
origins = os.getenv("CORS_ORIGINS", default_origins).split(",")

print(f"CORS allowed origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(data.router, prefix="/api/data", tags=["Data"])
app.include_router(predictions.router, prefix="/api/predict", tags=["Predictions"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(approvals.router, prefix="/api/approvals", tags=["Approvals"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])


@app.get("/")
async def root():
    return {
        "message": "ICT Impact Assessment API",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "AI-powered predictions",
            "Admin approval workflow",
            "Real-time notifications",
            "Advanced analytics"
        ]
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": f"Internal server error: {str(exc)}"},
    )
