"""
Triple C Consulting - Contact Form API
FastAPI backend for handling contact form submissions
"""

from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime, timedelta
from typing import Optional, List
import os
from dotenv import load_dotenv
import logging
from collections import defaultdict
import asyncio

from database import Database, ContactSubmission
from email_service import EmailService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Triple C Contact API",
    description="Contact form submission API for cccops.com",
    version="1.0.0"
)

# CORS configuration - allow cccops.com and localhost for testing
ALLOWED_ORIGINS = [
    "https://cccops.com",
    "https://www.cccops.com",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["*"],
)

# Rate limiting storage (in production, use Redis)
rate_limit_storage = defaultdict(list)
RATE_LIMIT_REQUESTS = 5
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds

# Initialize services
db = Database()
email_service = EmailService()

# API Key authentication
API_KEY = os.getenv("ADMIN_API_KEY", "your-secure-api-key-change-in-production")


# Pydantic models
class ContactRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    organization: Optional[str] = Field(None, max_length=200)
    message: str = Field(..., min_length=10, max_length=5000)
    honeypot: Optional[str] = Field(None, alias="_gotcha")

    @validator('name', 'message')
    def strip_whitespace(cls, v):
        if v:
            return v.strip()
        return v

    @validator('organization')
    def strip_organization(cls, v):
        if v:
            return v.strip()
        return v or None


class ContactResponse(BaseModel):
    success: bool
    message: str
    submission_id: Optional[int] = None


class UpdateStatusRequest(BaseModel):
    status: str = Field(..., pattern="^(new|contacted|resolved|spam)$")


class SubmissionResponse(BaseModel):
    id: int
    name: str
    email: str
    organization: Optional[str]
    message: str
    created_at: str
    ip_address: str
    status: str


# Middleware and dependencies
def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host


def check_rate_limit(ip_address: str) -> bool:
    """Check if IP address has exceeded rate limit"""
    now = datetime.now()
    cutoff = now - timedelta(seconds=RATE_LIMIT_WINDOW)

    # Clean old entries
    rate_limit_storage[ip_address] = [
        timestamp for timestamp in rate_limit_storage[ip_address]
        if timestamp > cutoff
    ]

    # Check if limit exceeded
    if len(rate_limit_storage[ip_address]) >= RATE_LIMIT_REQUESTS:
        return False

    # Add current request
    rate_limit_storage[ip_address].append(now)
    return True


def verify_api_key(x_api_key: str = Header(...)) -> bool:
    """Verify API key for admin endpoints"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


# Routes
@app.get("/")
async def root():
    """API health check"""
    return {
        "service": "Triple C Contact API",
        "status": "operational",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        db.get_all_submissions(limit=1)
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"

    return {
        "status": "ok",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/contact", response_model=ContactResponse)
async def submit_contact_form(
    contact: ContactRequest,
    request: Request
):
    """
    Handle contact form submissions
    - Validates input
    - Checks honeypot for spam
    - Applies rate limiting
    - Stores in database
    - Sends notification emails
    """
    try:
        # Spam check - honeypot field
        if contact.honeypot:
            logger.warning(f"Honeypot triggered for email: {contact.email}")
            # Return success to fool bots
            return ContactResponse(
                success=True,
                message="Thank you for your message. We'll be in touch soon."
            )

        # Rate limiting
        client_ip = get_client_ip(request)
        if not check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )

        # Store in database
        submission_id = db.create_submission(
            name=contact.name,
            email=contact.email,
            organization=contact.organization,
            message=contact.message,
            ip_address=client_ip
        )

        logger.info(f"New submission #{submission_id} from {contact.email}")

        # Send notification emails asynchronously
        asyncio.create_task(
            send_notification_emails(
                submission_id=submission_id,
                name=contact.name,
                email=contact.email,
                organization=contact.organization,
                message=contact.message
            )
        )

        return ContactResponse(
            success=True,
            message="Thank you for your message. We'll be in touch within 24 hours.",
            submission_id=submission_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing contact form: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred processing your request. Please try again."
        )


async def send_notification_emails(
    submission_id: int,
    name: str,
    email: str,
    organization: Optional[str],
    message: str
):
    """Send notification emails to owner and customer"""
    try:
        # Send notification to owner
        await email_service.send_owner_notification(
            submission_id=submission_id,
            name=name,
            email=email,
            organization=organization,
            message=message
        )

        # Send confirmation to customer
        await email_service.send_customer_confirmation(
            name=name,
            email=email
        )

        logger.info(f"Notification emails sent for submission #{submission_id}")

    except Exception as e:
        logger.error(f"Error sending emails for submission #{submission_id}: {e}")
        # Don't raise - email failure shouldn't fail the submission


@app.get("/api/submissions", response_model=List[SubmissionResponse])
async def get_submissions(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Get all submissions (admin only)
    Requires X-API-Key header
    """
    try:
        submissions = db.get_all_submissions(limit=limit, offset=offset, status=status)
        return [
            SubmissionResponse(
                id=sub.id,
                name=sub.name,
                email=sub.email,
                organization=sub.organization,
                message=sub.message,
                created_at=sub.created_at,
                ip_address=sub.ip_address,
                status=sub.status
            )
            for sub in submissions
        ]
    except Exception as e:
        logger.error(f"Error retrieving submissions: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving submissions")


@app.get("/api/submissions/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: int,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Get a specific submission by ID (admin only)
    Requires X-API-Key header
    """
    try:
        submission = db.get_submission_by_id(submission_id)
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")

        return SubmissionResponse(
            id=submission.id,
            name=submission.name,
            email=submission.email,
            organization=submission.organization,
            message=submission.message,
            created_at=submission.created_at,
            ip_address=submission.ip_address,
            status=submission.status
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving submission {submission_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving submission")


@app.patch("/api/submissions/{submission_id}/status")
async def update_submission_status(
    submission_id: int,
    status_update: UpdateStatusRequest,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Update submission status (admin only)
    Requires X-API-Key header
    """
    try:
        success = db.update_submission_status(submission_id, status_update.status)
        if not success:
            raise HTTPException(status_code=404, detail="Submission not found")

        logger.info(f"Updated submission #{submission_id} status to: {status_update.status}")

        return {
            "success": True,
            "message": f"Status updated to {status_update.status}",
            "submission_id": submission_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating submission {submission_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating submission")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting Contact API...")
    db.init_db()
    logger.info("Database initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Contact API...")
    db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
