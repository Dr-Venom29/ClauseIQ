from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.routes import documents, chat, summary, checklist, risks, export, comparison, metrics, auth, search, dashboard, activity
from app.core.config import settings
from app.db.session import engine
from app.models.document import Base
from app.models.user import User
from app.models.activity_log import ActivityLog
from app.core.exceptions import QuotaExceededException
import os
from sqlalchemy import create_engine, inspect

# Dynamic schema migration/recreation check for SQLite
if settings.DATABASE_URL.startswith("sqlite"):
    db_file = settings.DATABASE_URL.replace("sqlite:///", "")
    # Convert to absolute path to ensure robustness regardless of execution directory
    if not os.path.isabs(db_file):
        db_file = os.path.abspath(db_file)
    if os.path.exists(db_file):
        try:
            temp_engine = create_engine(settings.DATABASE_URL)
            inspector = inspect(temp_engine)
            if "documents" in inspector.get_table_names():
                columns = [c["name"] for c in inspector.get_columns("documents")]
                if "user_id" not in columns:
                    print(f"Outdated database schema detected (missing user_id). Wiping {db_file}...")
                    temp_engine.dispose()
                    for file_to_del in [db_file, "faiss_index.bin", "faiss_metadata.pkl"]:
                        if os.path.exists(file_to_del):
                            try:
                                os.remove(file_to_del)
                            except Exception as e:
                                print(f"Could not remove {file_to_del}: {e}")
            else:
                temp_engine.dispose()
        except Exception as e:
            print(f"Error checking database schema: {e}")

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.exception_handler(QuotaExceededException)
async def quota_exceeded_handler(request: Request, exc: QuotaExceededException):
    return JSONResponse(
        status_code=429,
        content={
            "status": "quota_exceeded",
            "message": exc.message,
            "retry_later": True
        }
    )

app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(summary.router, prefix="/api/v1", tags=["summary"])
app.include_router(checklist.router, prefix="/api/v1", tags=["checklist"])
app.include_router(risks.router, prefix="/api/v1", tags=["risks"])
app.include_router(export.router, prefix="/api/v1", tags=["export"])
app.include_router(comparison.router, prefix="/api/v1", tags=["comparison"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["metrics"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["dashboard"])
app.include_router(activity.router, prefix="/api/v1", tags=["activity"])

@app.get("/")
async def root():
    return {"message": "Welcome to ClauseIQ"}
