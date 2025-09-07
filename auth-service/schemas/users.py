from pydantic import BaseModel, Field, ValidationError, EmailStr ,model_validator


class UserBase(BaseModel):
    username: str
    email: EmailStr | None = Field(default = None)
    phone: str | None = Field(
        pattern=r"^09\d{9}$",
        title="Only IR phone number",
        description="A 11 character phone numbers",
        default= None
    )

class UserCreate(UserBase):
    password: str
    confirm_password: str

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'UserCreate':
        """Ensure the two password fields match."""
        pw1 = self.password
        pw2 = self.confirm_password
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError('Passwords do not match')
        return self

class UserRead(UserBase):
    id: int

class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    phone: str | None = Field(
        pattern=r"^09\d{9}$",
        title="Only IR phone number",
        description="A 11 character phone numbers",
        default=None
    )

class UserPasswordChange(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'UserPasswordChange':
        """Ensure the two password fields match."""
        pw1 = self.new_password
        pw2 = self.confirm_password
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError('Passwords do not match')
        return self

class UserLogin(BaseModel):
    username: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    password: str

    @model_validator(mode='after')
    def check_login_input(self) -> 'UserLogin':
        username = self.username
        phone = self.phone
        email = self.email
        if username is None and phone is None and email is None:
            raise ValueError('atleast one of the fields is required')
        return self






