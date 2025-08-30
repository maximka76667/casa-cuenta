import os
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer
from jose import jwt
import httpx
from dotenv import load_dotenv
from dependencies import supabase
from fastapi.middleware.cors import CORSMiddleware

from models.auth import AuthCredentials

from routers import expenses
from routers import groups
from routers import debtors
from routers import persons
from routers import members
from routers import users

load_dotenv()


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

origins = [
    "http://localhost:5173",
    "http://localhost:12000",
    "http://localhost:12001",
    "http://localhost:12006",
    "http://localhost:12007",
    "https://work-1-azccrmdytbbrmuij.prod-runtime.all-hands.dev",
]

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def hello():
    return {"message": "Hello!"}


# Auth
@app.post("/signup")
def signup(auth: AuthCredentials):
    user = supabase.auth.sign_up(
        {"email": auth.email, "password": auth.password, "email_confirm": False}
    )
    return {"user": user}


@app.post("/signin")
def signin(auth: AuthCredentials):
    response = supabase.auth.sign_in_with_password(
        {
            "email": auth.email,
            "password": auth.password,
        }
    )
    return {"user": response.user, "access_token": response.session.access_token}


app.include_router(expenses.router)
app.include_router(groups.router)
app.include_router(debtors.router)
app.include_router(persons.router)
app.include_router(members.router)
app.include_router(users.router)
