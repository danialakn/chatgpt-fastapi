from fastapi import Depends
from sqlmodel import Session
from typing import Annotated
from database import get_session

from passlib.context import CryptContext

SessionDep = Annotated[Session, Depends(get_session)]

pwd_context = CryptContext(schemes=["sha256_crypt"])
class Hasher:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
