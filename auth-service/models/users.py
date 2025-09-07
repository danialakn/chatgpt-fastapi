from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int | None= Field(default=None ,primary_key=True)
    username: str = Field(index=True ,unique=True)
    email: str | None = Field(default=None, unique=True)
    phone: str | None = Field(default=None, unique=True)
    password: str
