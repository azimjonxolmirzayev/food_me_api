from pydantic import BaseModel
from typing import Optional


class SignUpModel(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                'username': "foodme",
                'email': "foodme@gmail.com",
                'password': "foodme1234",
            }
        }


class Settings(BaseModel):
    authjwt_secret_key: str = '661929cfafb3c51f6a35939a5476ec18a59b7db5f1ba27952950e1145104ca3b'


class LoginModel(BaseModel):
    username_or_email: str
    password: str


class CafeCreate(BaseModel):
    name: str
    location: str
    description: Optional[str] = None
    phonenumber: str
    wifipass: Optional[str] = None
    logo_url: Optional[str] = None
    image_url: Optional[str] = None


class CafeResponse(BaseModel):
    id: int
    name: str
    location: str
    description: str
    phonenumber: str
    wifipass: str
    logo_url: str
    image_url: str

    class Config:
        orm_mode = True


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: int
    menu_id: int
    cafe_id: int
    image_url: Optional[str] = None
    ingredients: Optional[str] = None

    class Config:
        orm_mode = True


class MenuResponse(BaseModel):
    id: int
    name: str
    cafe_id: int

    class Config:
        orm_mode = True


class CafeUpdate(BaseModel):
    new_name: str


class MenuCreate(BaseModel):
    name: str
    cafe_id: int

    class Config:
        orm_mode = True


class MenuUpdate(BaseModel):
    name: str

    class Config:
        orm_mode = True


class UpdateCafeRequest(BaseModel):
    name: str
    location: str
    description: str
    phonenumber: str
    wifipass: str
    logo_url: str
    image_url: str


class ProductCreate(BaseModel):
    name: str
    price: float
    description: str = None  # Optional field
    menu_id: int
    cafe_id: int

    class Config:
        orm_mode = True
