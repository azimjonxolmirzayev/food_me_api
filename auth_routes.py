from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from schemas import SignUpModel, LoginModel
from database import session, engine
from model import User
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT
from fastapi.responses import JSONResponse

from sqlalchemy import or_

auth_router = APIRouter(
    prefix="/auth"
)

session = session(bind=engine)


@auth_router.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(user: SignUpModel):
    db_email = session.query(User).filter(User.email == user.email).first()
    if db_email is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Allaqachon email ishlatilgan :(")

    db_username = session.query(User).filter(User.username == user.username).first()
    if db_username is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Allaqachon ism ishlatilgan :(")

    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password)
    )

    session.add(new_user)
    session.commit()
    data = {
        "id": new_user.id,
        "username": new_user.username,
        "email": user.email
    }

    response_model = {
        "success": True,
        "code": 201,
        "message": "User is created successfully",
        "data": data
    }

    return response_model


@auth_router.post('/login', status_code=200)
async def login(user: LoginModel, Authorize: AuthJWT = Depends()):
    db_user = session.query(User).filter(
        or_(
            User.username == user.username_or_email,
            User.email == user.username_or_email
        )
    ).first()

    if db_user and check_password_hash(db_user.password, user.password):
        access_token = Authorize.create_access_token(subject=db_user.username)
        refresh_token = Authorize.create_refresh_token(subject=db_user.username)

        token = {
            "access": access_token,
            "refresh": refresh_token
        }

        response = {
            "success": True,
            "code": 200,
            "message": "User successfully logged in",
            "data": {
                "token": token,
                "user": {
                    "id": db_user.id,
                    "username": db_user.username,
                    "email": db_user.email
                }
            }
        }

        return jsonable_encoder(response)

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")