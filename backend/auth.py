import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt


# ---------------------------------------------------------
# Load .env from the backend directory
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_FILE)


# ---------------------------------------------------------
# Authentication configuration
# ---------------------------------------------------------

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is not configured in the environment."
    )

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


oauth2_scheme = HTTPBearer()


# ---------------------------------------------------------
# Demo credentials
# ---------------------------------------------------------

DEMO_USERNAME = os.getenv(
    "DEMO_USERNAME",
    "demo"
)

DEMO_PASSWORD = os.getenv(
    "DEMO_PASSWORD"
)

if not DEMO_PASSWORD:
    raise RuntimeError(
        "DEMO_PASSWORD is not configured in the environment."
    )


# ---------------------------------------------------------
# Create JWT token
# ---------------------------------------------------------

def create_access_token(username: str):
    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": username,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ---------------------------------------------------------
# Authenticate demo user
# ---------------------------------------------------------

def authenticate_user(
    username: str,
    password: str
):
    if (
        username == DEMO_USERNAME
        and password == DEMO_PASSWORD
    ):
        return username

    return None


# ---------------------------------------------------------
# Validate JWT token
# ---------------------------------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        oauth2_scheme
    )
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise credentials_exception

        return username

    except JWTError:
        raise credentials_exception
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise credentials_exception

        return username

    except JWTError:
        raise credentials_exception