from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from C7.authentication.password import verify_password
from C7.authentication.models import AccessToken, User


async def authenticate(session: AsyncSession, email: str, password: str) -> User | None:
    select_query = select(User).where(User.email == email)
    result = await session.execute(select_query)
    user: User | None = result.scalar_one_or_none()
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def create_access_token(session: AsyncSession, user: User) -> AccessToken:
    access_token = AccessToken(user=user)
    session.add(access_token)
    await session.commit()
    await session.refresh(access_token)
    return access_token
