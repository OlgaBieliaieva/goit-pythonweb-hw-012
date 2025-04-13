from datetime import datetime, timezone, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, Request, File, UploadFile
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi.middleware.cors import CORSMiddleware

from src.database.db import get_db, sessionmanager
from src.routes import contacts, auth, users

scheduler = AsyncIOScheduler()

async def cleanup_expired_tokens():
    """
    Clean up expired refresh tokens from the database.

    This function removes refresh tokens that have expired or have been revoked.
    It runs periodically to ensure the database is free from expired tokens.
    """
    async with sessionmanager.session() as db:
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=7)
        stmt = text(
            "DELETE FROM refresh_tokens WHERE expired_at < :now OR revoked_at IS NOT NULL AND revoked_at < :cutoff"
        )
        await db.execute(stmt, {"now": now, "cutoff": cutoff})
        await db.commit()
        print(f"Expired tokens cleaned up [{now.strftime('%Y-%m-%d %H:%M:%S')}]")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the lifespan of the FastAPI application.

    This context manager initializes the scheduler to periodically clean up expired tokens
    and shuts down the scheduler when the application is stopped.
    """
    scheduler.add_job(cleanup_expired_tokens, "interval", hours=1)
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(
    lifespan=lifespan,
    title="Contact Book Application",
    description="Contact Book Application",
    version="0.1.0",
)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Handles RateLimitExceeded exceptions by returning a custom error message.

    Args:
        request: The request object.
        exc: The exception raised by the slowapi rate limiter.

    Returns:
        A JSON response indicating that the rate limit has been exceeded.
    """
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Перевищено ліміт запитів. Спробуйте пізніше."},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")


@app.get("/")
def read_root(request: Request):
    """
    Root endpoint that returns a welcome message.

    Returns:
        A dictionary with a welcome message.
    """
    return {"message": "Contact book application v.0.1.0"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint to verify the status of the application and database.

    This endpoint runs a simple query on the database to ensure the connection
    is active and correctly configured.

    Args:
        db: The database session to execute the query.

    Returns:
        A dictionary with a success message if the database connection is valid.

    Raises:
        HTTPException: If the database is not correctly configured or if the connection fails.
    """
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )