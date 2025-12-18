"""
Database module for contact form submissions
Uses SQLite for simplicity and portability
"""

import sqlite3
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ContactSubmission:
    """Data class for contact submissions"""
    id: int
    name: str
    email: str
    organization: Optional[str]
    message: str
    created_at: str
    ip_address: str
    status: str


class Database:
    """SQLite database handler for contact submissions"""

    def __init__(self, db_path: str = "contact_submissions.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None

    def get_connection(self) -> sqlite3.Connection:
        """Get or create database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def init_db(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create submissions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                organization TEXT,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'new'
            )
        """)

        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_submissions_created_at
            ON submissions(created_at DESC)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_submissions_status
            ON submissions(status)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_submissions_email
            ON submissions(email)
        """)

        conn.commit()
        logger.info("Database schema initialized")

    def create_submission(
        self,
        name: str,
        email: str,
        organization: Optional[str],
        message: str,
        ip_address: str
    ) -> int:
        """
        Create a new contact submission
        Returns the submission ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        created_at = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO submissions (name, email, organization, message, created_at, ip_address, status)
            VALUES (?, ?, ?, ?, ?, ?, 'new')
        """, (name, email, organization, message, created_at, ip_address))

        conn.commit()
        submission_id = cursor.lastrowid

        logger.info(f"Created submission #{submission_id}")
        return submission_id

    def get_submission_by_id(self, submission_id: int) -> Optional[ContactSubmission]:
        """Get a submission by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, email, organization, message, created_at, ip_address, status
            FROM submissions
            WHERE id = ?
        """, (submission_id,))

        row = cursor.fetchone()
        if row:
            return ContactSubmission(**dict(row))
        return None

    def get_all_submissions(
        self,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None
    ) -> List[ContactSubmission]:
        """
        Get all submissions with optional filtering
        Returns most recent first
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        if status:
            cursor.execute("""
                SELECT id, name, email, organization, message, created_at, ip_address, status
                FROM submissions
                WHERE status = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (status, limit, offset))
        else:
            cursor.execute("""
                SELECT id, name, email, organization, message, created_at, ip_address, status
                FROM submissions
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))

        rows = cursor.fetchall()
        return [ContactSubmission(**dict(row)) for row in rows]

    def update_submission_status(self, submission_id: int, status: str) -> bool:
        """
        Update the status of a submission
        Returns True if successful, False if submission not found
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE submissions
            SET status = ?
            WHERE id = ?
        """, (status, submission_id))

        conn.commit()

        if cursor.rowcount > 0:
            logger.info(f"Updated submission #{submission_id} status to: {status}")
            return True
        return False

    def get_submission_count(self, status: Optional[str] = None) -> int:
        """Get total count of submissions, optionally filtered by status"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if status:
            cursor.execute("SELECT COUNT(*) FROM submissions WHERE status = ?", (status,))
        else:
            cursor.execute("SELECT COUNT(*) FROM submissions")

        return cursor.fetchone()[0]

    def get_submissions_by_email(self, email: str) -> List[ContactSubmission]:
        """Get all submissions from a specific email address"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, email, organization, message, created_at, ip_address, status
            FROM submissions
            WHERE email = ?
            ORDER BY created_at DESC
        """, (email,))

        rows = cursor.fetchall()
        return [ContactSubmission(**dict(row)) for row in rows]

    def get_submissions_by_ip(self, ip_address: str, hours: int = 24) -> List[ContactSubmission]:
        """Get submissions from an IP address within the last N hours"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cutoff = datetime.now().replace(microsecond=0) - timedelta(hours=hours)
        cutoff_str = cutoff.isoformat()

        cursor.execute("""
            SELECT id, name, email, organization, message, created_at, ip_address, status
            FROM submissions
            WHERE ip_address = ? AND created_at > ?
            ORDER BY created_at DESC
        """, (ip_address, cutoff_str))

        rows = cursor.fetchall()
        return [ContactSubmission(**dict(row)) for row in rows]

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Database connection closed")


# For testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    db = Database("test_contact.db")
    db.init_db()

    # Test create
    submission_id = db.create_submission(
        name="Test User",
        email="test@example.com",
        organization="Test Corp",
        message="This is a test message",
        ip_address="127.0.0.1"
    )

    print(f"Created submission: {submission_id}")

    # Test get by ID
    submission = db.get_submission_by_id(submission_id)
    print(f"Retrieved submission: {submission}")

    # Test get all
    all_submissions = db.get_all_submissions()
    print(f"All submissions: {len(all_submissions)}")

    # Test update status
    db.update_submission_status(submission_id, "contacted")
    updated = db.get_submission_by_id(submission_id)
    print(f"Updated status: {updated.status}")

    db.close()
