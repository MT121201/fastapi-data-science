import contextlib
from datetime import datetime, timezone

from fastapi import FastAPI, Form, HTTPException, status, Response, Depends
from fastapi.security import APIKeyCookie
from sqlalchemy import select, exc
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware
from starlette_csrf import CSRFMiddleware

from C7.csrf import schemas
from C7.csrf.database import create_all_tables, get_async_session
from C7.csrf.authentication import authenticate, create_access_token
from C7.csrf.models import AccessToken, User
from C7.csrf.password import get_password_hash

TOKEN_COOKIE_NAME = "access_token"
CSRF_TOKEN_SECRET = "secret"

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    await create_all_tables()
    yield


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CSRFMiddleware,
    secret=CSRF_TOKEN_SECRET,
    sensitive_cookies={TOKEN_COOKIE_NAME},
    cookie_domain="localhost",
)

async def get_current_user(token: str = Depends(APIKeyCookie(name=TOKEN_COOKIE_NAME)),
                           session: AsyncSession = Depends(get_async_session)) -> User:
    query = select(AccessToken).where(AccessToken.access_token == token,
                                      AccessToken.expiration_date>=(datetime.now(tz=timezone.utc)))
    result = await session.execute(query)
    token: AccessToken|None = result.scalar_one_or_none()
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return token.user


@app.get("/csrf_token")
async def csrf_token():
    return None


@app.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.UserRead)
async def register(
        user_create: schemas.UserCreate,
        session: AsyncSession = Depends(get_async_session)
)->User:
    hashed_password = get_password_hash(user_create.password)
    user = User(**user_create.model_dump(exclude={"password"}), hashed_password=hashed_password)

    try:
        session.add(user)
        await session.commit()
    except exc.IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    return user


@app.post("/login")
async def login(
        response: Response,
        email: str = Form(...),
        password: str = Form(...),
        session: AsyncSession = Depends(get_async_session)
):
    user = await authenticate(session=session, email=email, password=password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    token = await create_access_token(user=user, session=session)
    response.set_cookie(key=TOKEN_COOKIE_NAME,
                        value=token.access_token,
                        max_age= token.max_age(),
                        secure=True,
                        samesite="lax",
                        httponly=True)
    return {"detail": "Login successful"}


@app.get("/me", response_model=schemas.UserRead)
async def get_me(user: User = Depends(get_current_user)):
    return user


@app.post("/me", response_model=schemas.UserRead)
async def update_me(user_update: schemas.UserUpdate,
                    user: User = Depends(get_current_user),
                    session: AsyncSession = Depends(get_async_session)):
    user_update_dict = user_update.model_dump(exclude_unset=True)
    for key, value in user_update_dict.items():
        setattr(user, key, value)
    session.add(user)
    await session.commit()
    await session.refresh(user)
