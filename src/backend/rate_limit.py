from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import Request, HTTPException, status

class RateLimiter:
    def __init__(self, window_minutes: int = 15, max_attempts: int = 5):
        self.window_minutes = window_minutes
        self.max_attempts = max_attempts
        self.attempts: Dict[str, List[datetime]] = {}

    def _clean_old_attempts(self, key: str) -> None:
        """Remove attempts outside the current window"""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=self.window_minutes)
        self.attempts[key] = [
            attempt for attempt in self.attempts.get(key, [])
            if attempt > window_start
        ]

    def check_rate_limit(self, username: str, request: Request) -> None:
        """
        Check if the current request exceeds rate limits.
        Raises HTTPException if rate limit is exceeded.
        """
        key = f"{username}:{request.client.host}"
        self._clean_old_attempts(key)

        if len(self.attempts.get(key, [])) >= self.max_attempts:
            wait_minutes = self.window_minutes - (
                datetime.utcnow() - min(self.attempts[key])
            ).total_seconds() / 60
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many login attempts. Please try again in {int(wait_minutes)} minutes."
            )

    def record_attempt(self, username: str, request: Request) -> None:
        """Record a failed login attempt"""
        key = f"{username}:{request.client.host}"
        if key not in self.attempts:
            self.attempts[key] = []
        self.attempts[key].append(datetime.utcnow())

    def clear_attempts(self, username: str, request: Request) -> None:
        """Clear attempts after successful login"""
        key = f"{username}:{request.client.host}"
        self.attempts.pop(key, None)

# Create a global rate limiter instance
login_rate_limiter = RateLimiter()
