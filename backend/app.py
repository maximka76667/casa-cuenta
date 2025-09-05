import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.security import HTTPBearer
from jose import jwt
import httpx
from dotenv import load_dotenv
from dependencies import supabase
from fastapi.middleware.cors import CORSMiddleware

from prometheus_fastapi_instrumentator import Instrumentator

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from models.auth import AuthCredentials

from middlewares.monitoring import metrics_endpoint, monitoring_middleware
from middlewares.logger import get_logger, log_auth_event

from middlewares.rate_limiter import (
    auth_rate_limit,
    basic_rate_limit,
    init_rate_limiter,
    limiter,
    rate_limit_exceeded_handler,
)
from routers import expenses
from routers import groups
from routers import debtors
from routers import persons
from routers import group_users
from routers import users

origins = [
    "http://localhost:5173",
    "http://localhost:12000",
    "http://localhost:12001",
    "http://localhost:12006",
    "http://localhost:12007",
    "https://work-1-azccrmdytbbrmuij.prod-runtime.all-hands.dev",
]

load_dotenv()

logger = get_logger()

app = FastAPI()
security = HTTPBearer()


# jwks_cache = None

# async def get_jwks():
#     global jwks_cache
#     if jwks_cache is None:
#         async with httpx.AsyncClient() as client:
#             resp = await client.get(SUPABASE_JWKS_URL)
#             resp.raise_for_status()
#             jwks_cache = resp.json()
#     return jwks_cache

# async def verify_jwt(credentials=Depends(security)):
#     token = credentials.credentials
#     jwks = await get_jwks()

#     try:
#         payload = jwt.decode(
#             token,
#             jwks,
#             algorithms=["RS256"],
#             audience=f"https://{SUPABASE_PROJECT_ID}.supabase.co/auth/v1"
#         )
#         return payload
#     except Exception:
#         raise HTTPException(status_code=401, detail="Invalid token")


# Initialize rate limiter
@app.on_event("startup")
async def startup_event():
    await init_rate_limiter()
    logger.info("Application startup completed")


# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


# Add monitoring middleware
app.middleware("http")(monitoring_middleware)

# Initialize Prometheus instrumentator
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)


@app.get("/metrics")
async def get_metrics():
    return await metrics_endpoint()


# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
@basic_rate_limit()
async def hello(request: Request):
    logger.info("Hello endpoint called")
    return {"message": "Hello!"}


# Auth
@app.post("/signup")
@auth_rate_limit()
def signup(auth: AuthCredentials, request: Request):
    try:
        logger.info(f"Signup attempt for email: {auth.email}")
        user = supabase.auth.sign_up(
            {"email": auth.email, "password": auth.password, "email_confirm": False}
        )
        log_auth_event("signup", auth.email, True)
        logger.info(f"Successful signup for email: {auth.email}")
        return {"user": user}
    except Exception as e:
        log_auth_event("signup", auth.email, False)
        logger.error(f"Signup failed for email: {auth.email} | Error: {str(e)}")
        raise HTTPException(status_code=400, detail="Signup failed")


@app.post("/signin")
@auth_rate_limit()
def signin(auth: AuthCredentials, request: Request):
    try:
        logger.info(f"Signin attempt for email: {auth.email}")
        response = supabase.auth.sign_in_with_password(
            {
                "email": auth.email,
                "password": auth.password,
            }
        )
        log_auth_event("signin", auth.email, True)
        logger.info(f"Successful signin for email: {auth.email}")
        return {"user": response.user, "access_token": response.session.access_token}
    except Exception as e:
        log_auth_event("signin", auth.email, False)
        logger.error(f"Signin failed for email: {auth.email} | Error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid credentials")


app.include_router(expenses.router)
app.include_router(groups.router)
app.include_router(debtors.router)
app.include_router(persons.router)
app.include_router(group_users.router)
app.include_router(users.router)
