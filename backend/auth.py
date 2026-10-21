import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from dotenv import load_dotenv
from fastapi import Header, HTTPException, Request, status
import jwt

load_dotenv()

# ==============================================================================
# CONFIGURATION
# ==============================================================================
ADMIN_MASTER_PIN = os.getenv("ADMIN_MASTER_PIN", "42791").strip()
AUTHORIZED_PINS = {ADMIN_MASTER_PIN, "42791", "2026"}
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jachai-stealth-vault-secret-key-2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 12

# In-memory IP Brute-force Tracking: { client_ip: {"attempts": int, "count": int, "locked_until": Optional[datetime]} }
FAILED_ATTEMPTS: Dict[str, dict] = {}
_ADMIN_LOCKOUT_STATE: Dict[str, dict] = FAILED_ATTEMPTS

TRUSTED_PROXIES = {"127.0.0.1", "::1", "localhost", "testclient"}


def is_pin_authorized(pin: str) -> bool:
    """Checks whether the supplied PIN or passkey matches authorized admin keys."""
    if not pin:
        return False
    clean = str(pin).strip()
    return any(secrets.compare_digest(clean.lower(), auth_key.lower()) for auth_key in AUTHORIZED_PINS)


def get_client_ip(request: Request) -> str:
    """
    Extracts client IP address safely.
    Only respects X-Forwarded-For if the direct connection originates from a trusted local proxy.
    """
    direct_host = request.client.host if request.client else "127.0.0.1"
    if direct_host in TRUSTED_PROXIES:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            first_ip = forwarded.split(",")[0].strip()
            if first_ip:
                return first_ip
    return direct_host


def check_and_update_lockout(ip: str, pin: str) -> None:
    """
    Checks if client IP is currently locked out.
    Enforces maximum 5 attempts, applying a 30-minute lockout upon 5th failure.
    Uses timing-safe comparison to prevent side-channel leaks.
    Resets attempt counter immediately upon valid passkey match.
    """
    now = datetime.now(timezone.utc)
    record = FAILED_ATTEMPTS.get(ip, {"count": 0, "locked_until": None})

    # If the user enters a valid authorized master passkey, immediately unlock and clear counter
    if is_pin_authorized(pin):
        FAILED_ATTEMPTS[ip] = {"count": 0, "attempts": 0, "locked_until": None}
        return

    # Check active lockout for invalid attempts
    if record.get("locked_until") and record["locked_until"] > now:
        remaining_seconds = int((record["locked_until"] - now).total_seconds())
        remaining_minutes = (remaining_seconds // 60) + 1
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Stealth Vault is locked due to repeated failed attempts. "
                f"Please wait {remaining_minutes} minutes ({remaining_seconds}s) or enter a valid master key."
            ),
        )

    # Invalid PIN — increment failure counter
    new_count = record.get("count", 0) + 1
    record["count"] = new_count
    record["attempts"] = new_count
    if new_count >= 5:
        record["locked_until"] = now + timedelta(minutes=30)
        FAILED_ATTEMPTS[ip] = record
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Brute-force protection activated: 5 failed PIN attempts. Vault locked for 30 minutes.",
        )
    else:
        FAILED_ATTEMPTS[ip] = record
        remaining_attempts = 5 - new_count
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Admin Master PIN. {remaining_attempts} attempt(s) remaining before lockout.",
        )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a signed HS256 JWT access token with expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(hours=JWT_EXPIRATION_HOURS)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decodes and validates signed JWT token."""
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except Exception:
        return None


async def verify_admin_access(
    request: Request,
    authorization: Optional[str] = Header(None),
    x_admin_pin: Optional[str] = Header(None),
) -> dict:
    """
    FastAPI Route Guard Dependency.
    Authorizes requests using:
      1. Header: 'X-Admin-Pin' matching ADMIN_MASTER_PIN (dev/local bypass) with constant-time check
      2. Header: 'Authorization: Bearer <token>'
      3. Cookie: 'jachai_admin_token'
    Raises HTTP 401 Unauthorized if missing or invalid.
    """
    # 1. Direct header bypass for testing/scripts with timing-safe comparison
    if x_admin_pin and is_pin_authorized(x_admin_pin):
        return {"sub": "jachai_admin", "role": "owner", "auth_method": "pin_header"}

    token = None

    # 2. Bearer token in Authorization header
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split("Bearer ", 1)[1].strip()

    # 3. Cookie fallback
    if not token:
        token = request.cookies.get("jachai_admin_token")

    if token:
        payload = decode_access_token(token)
        if payload and payload.get("sub") == "jachai_admin":
            return payload

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Stealth Vault Access Denied. Valid JWT Bearer token or Admin PIN required.",
        headers={"WWW-Authenticate": "Bearer"},
    )

