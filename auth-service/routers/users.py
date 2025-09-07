from fastapi import APIRouter,HTTPException, status, Depends
from sqlmodel import select
from sqlalchemy import and_, or_

from schemas.users import UserCreate, UserUpdate, UserRead, UserPasswordChange, UserLogin
from models.users import User
from dependencies import SessionDep, Hasher
from jwt_auth import sign_jwt, JWTBearer , decode_jwt
router = APIRouter()

@router.post("/users/create", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, session: SessionDep):
    """
    creates a new user.
    """
    user = User.model_validate(user)
    statement = select(User).where((User.username == user.username) | (User.email == user.email) | (User.phone == user.phone))
    existing_user = (await session.exec(statement)).first()

    if existing_user:
        if existing_user.username == user.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered."
            )
        elif existing_user.email == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered."
            )
        elif existing_user.phone and user.phone and existing_user.phone == user.phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already in use."
            )
    hashed_password = Hasher.get_password_hash(user.password)
    user_data = user.model_dump(exclude={"password", "confirm_password"})
    db_user = User(**user_data, password=hashed_password)

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user

@router.get("/users/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def read_user(user_id: int, session: SessionDep, token=Depends(JWTBearer())):
    """
    Get a single user by their ID.
    """
    user_identifier = str(decode_jwt(token)["user_id"])
    if str(user_id) != str(user_identifier):
        raise HTTPException(status_code=403, detail="not owner")

    user = await session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user



@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: int, session: SessionDep, token=Depends(JWTBearer())):
    user = await session.get(User, user_id)

    user_identifier = str(decode_jwt(token)["user_id"])
    if str(user_id) != str(user_identifier):
        raise HTTPException(status_code=403, detail="not owner")

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await session.delete(user)
    await session.commit()
    return {"ok": True, "message": "User deleted successfully"}
@router.patch("/users/password/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def change_user_password(user_id: int, password_data: UserPasswordChange, session: SessionDep, token=Depends(JWTBearer())):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_identifier = str(decode_jwt(token)["user_id"])
    if str(user_id) != str(user_identifier):
        raise HTTPException(status_code=403, detail="not owner")
    if not Hasher.verify_password(password_data.current_password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    hashed_password = Hasher.get_password_hash(password_data.new_password)
    user.password = hashed_password
    session.add(user)
    await session.commit()
    return


@router.patch("/users/{user_id}",response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user_update: UserUpdate, session: SessionDep, token=Depends(JWTBearer())):
    user_identifier = str(decode_jwt(token)["user_id"])
    db_user = await session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if str(user_id) != str(user_identifier):
        raise HTTPException(status_code=403, detail="not owner")

    update_data = user_update.model_dump(exclude_unset=True)

    if update_data:
        or_conditions = []
        if "username" in update_data:
            or_conditions.append(User.username == update_data["username"])
        if "email" in update_data:
            or_conditions.append(User.email == update_data["email"])
        if "phone" in update_data and update_data["phone"] is not None:
            or_conditions.append(User.phone == update_data["phone"])

        if or_conditions:
            statement = select(User).where(and_(
                User.id != user_id,
                or_(*or_conditions)
            ))
            existing_user = (await session.exec(statement)).first()

            if existing_user:
                if "username" in update_data and existing_user.username == update_data["username"]:
                    raise HTTPException(status_code=400, detail="Username already registered.")
                if "email" in update_data and existing_user.email == update_data["email"]:
                    raise HTTPException(status_code=400, detail="Email already registered.")
                if "phone" in update_data and existing_user.phone == update_data["phone"]:
                    raise HTTPException(status_code=400, detail="Phone number already in use.")

    db_user.sqlmodel_update(update_data)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.post("/users/login", status_code=status.HTTP_200_OK)
async def login_user(login_data: UserLogin, session: SessionDep):

    statement = select(User).where((User.username == login_data.username) | (User.email == login_data.email) | (User.phone == login_data.phone))
    db_user = (await session.exec(statement)).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Incorrect user or password")
    if not Hasher.verify_password(login_data.password, db_user.password):
        raise HTTPException(status_code=404, detail="Incorrect user or password")
    return sign_jwt(user_id=db_user.id, username=db_user.username)
