import contextlib
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import exc, select
from sqlalchemy.ext.asyncio import AsyncSession

from C7.authentication import schemas
from C7.authentication.password import get_password_hash
from C7.authentication.database import create_all_tables, get_async_session
from C7.authentication.models import User, AccessToken
from C7.authentication.authentication import authenticate, create_access_token


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    await create_all_tables()
    yield

app = FastAPI(lifespan=lifespan)


async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/token")),
                           session: AsyncSession = Depends(get_async_session))->User:
    query = select(AccessToken).where(AccessToken.access_token == token,
                                      AccessToken.expiration_date>=(datetime.now(tz=timezone.utc)))
    result = await session.execute(query)
    token: AccessToken|None = result.scalar_one_or_none()
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return token.user


@app.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    return user


@app.post("/token")
async def create_token(
        from_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
        session: AsyncSession = Depends(get_async_session)
):
    email = from_data.username
    password = from_data.password
    user = await authenticate(email=email, password=password, session=session)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    token = await create_access_token(user=user, session=session)
    return {"access_token": token.access_token, "token_type": "bearer"}


@app.get("/protect_route", response_model=schemas.UserRead)
async def protect_route(user: User = Depends(get_current_user)):
    return user