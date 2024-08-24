import io

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse
import qrcode

from database import session, engine
from model import Cafes, User, Products, Menu
from schemas import CafeCreate, CafeResponse, ProductResponse, MenuResponse, CafeUpdate, UpdateCafeRequest, MenuCreate, \
    MenuUpdate, ProductCreate
from fastapi_jwt_auth import AuthJWT

kaffe_routes = APIRouter(
    prefix="/cafes"
)


def get_session():
    db = session(bind=engine)
    try:
        yield db
    finally:
        db.close()


@kaffe_routes.post('/', status_code=status.HTTP_201_CREATED)
async def create_cafe(cafe: CafeCreate, Authorize: AuthJWT = Depends(), db: session = Depends(get_session)):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()
    db_user = db.query(User).filter(User.username == current_user).first()

    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Foydalanuvchi topilmadi")

    existing_cafe = db.query(Cafes).filter(Cafes.owner_id == db_user.id).first()
    if existing_cafe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Foydalanuvchi allaqachon bir kafe yaratgan")

    new_cafe = Cafes(
        name=cafe.name,
        owner_id=db_user.id,
        location=cafe.location,
        description=cafe.description,
        phonenumber=cafe.phonenumber,
        wifipass=cafe.wifipass,
        logo_url=cafe.logo_url,
        image_url=cafe.image_url
    )

    db.add(new_cafe)
    db.commit()

    response = {
        "success": True,
        "code": 201,
        "message": "Kafe muvaffaqiyatli yaratildi",
        "data": jsonable_encoder(new_cafe)
    }

    return response


@kaffe_routes.get('/check', response_model=dict)
async def check_user_cafe(Authorize: AuthJWT = Depends(), db: session = Depends(get_session)):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()
    db_user = db.query(User).filter(User.username == current_user).first()

    if db_user is None:
        print("Foydalanuvchi topilmadi")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Foydalanuvchi topilmadi")

    existing_cafe = db.query(Cafes).filter(Cafes.owner_id == db_user.id).first()

    if existing_cafe is None:
        print("Kafe topilmadi")

    return {"has_cafe": existing_cafe is not None}


@kaffe_routes.get('/{cafe_id}', response_model=CafeResponse)
async def get_cafe(cafe_id: int, db: session = Depends(get_session)):
    cafe = db.query(Cafes).filter(Cafes.id == cafe_id).first()

    if cafe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kafe topilmadi")

    return jsonable_encoder(cafe)


@kaffe_routes.get('/{cafe_id}/menus/{menu_id}/products')
async def get_menu_products(cafe_id: int, menu_id: int, db: Session = Depends(get_session)):
    products = db.query(Products).filter(
        Products.menu_id == menu_id,
        Products.cafe_id == cafe_id
    ).all()
    if not products:
        raise HTTPException(status_code=404, detail="No products found")
    return products


@kaffe_routes.post('/{cafe_id}/menus/{menu_id}/products', response_model=ProductCreate)
async def create_product(
        cafe_id: int,
        menu_id: int,
        product: ProductCreate,
        db: Session = Depends(get_session)
):
    db_product = Products(
        name=product.name,
        price=product.price,
        description=product.description,
        menu_id=menu_id,
        cafe_id=cafe_id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@kaffe_routes.get("/generate-qrcode/{cafe_id}")
async def generate_qrcode(cafe_id: str):
    # QR kodni yaratamiz
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(f'https://example.com/cafe/{cafe_id}')  # Cafe URL yoki boshqa ma'lumot
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    # QR kodni PNG formatida saqlaymiz
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    # StreamingResponse orqali yuklash uchun javob qaytaramiz
    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename=cafe-{cafe_id}-qrcode.png"}
    )


@kaffe_routes.get('/{cafe_id}/menus', response_model=list[MenuResponse])
async def get_cafe_menus(cafe_id: int, db: Session = Depends(get_session)):
    menus = db.query(Menu).filter(Menu.cafe_id == cafe_id).all()

    if not menus:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menular topilmadi")

    return menus


@kaffe_routes.put('/{cafe_id}', response_model=CafeResponse)
async def update_cafe_name(cafe_id: int, cafe_update: CafeUpdate, Authorize: AuthJWT = Depends(),
                           db: Session = Depends(get_session)):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()
    db_user = db.query(User).filter(User.username == current_user).first()

    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Foydalanuvchi topilmadi")

    cafe = db.query(Cafes).filter(Cafes.id == cafe_id, Cafes.owner_id == db_user.id).first()

    if cafe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Kafe topilmadi yoki siz kafening egasi emassiz")

    cafe.name = cafe_update.name
    db.commit()
    db.refresh(cafe)

    return jsonable_encoder(cafe)


@kaffe_routes.get('/user/cafe', response_model=CafeResponse)
async def get_user_cafe(Authorize: AuthJWT = Depends(), db: Session = Depends(get_session)):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()
    db_user = db.query(User).filter(User.username == current_user).first()

    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Foydalanuvchi topilmadi")

    existing_cafe = db.query(Cafes).filter(Cafes.owner_id == db_user.id).first()

    if existing_cafe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kafe topilmadi")

    return jsonable_encoder(existing_cafe)


@kaffe_routes.put('/user/cafe', response_model=CafeResponse)
async def update_user_cafe(
        cafe_data: UpdateCafeRequest,
        Authorize: AuthJWT = Depends(),
        db: Session = Depends(get_session)
):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()
    db_user = db.query(User).filter(User.username == current_user).first()

    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Foydalanuvchi topilmadi")

    existing_cafe = db.query(Cafes).filter(Cafes.owner_id == db_user.id).first()

    if existing_cafe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kafe topilmadi")

    existing_cafe.name = cafe_data.name
    existing_cafe.location = cafe_data.location
    existing_cafe.description = cafe_data.description
    existing_cafe.phonenumber = cafe_data.phonenumber
    existing_cafe.wifipass = cafe_data.wifipass
    existing_cafe.logo_url = cafe_data.logo_url
    existing_cafe.image_url = cafe_data.image_url

    db.commit()
    db.refresh(existing_cafe)

    return jsonable_encoder(existing_cafe)


@kaffe_routes.post('/{cafe_id}/menus', response_model=MenuCreate)
async def create_menu(cafe_id: int, menu: MenuCreate, db: Session = Depends(get_session)):
    # Yangi menyu yaratish
    db_menu = Menu(name=menu.name, cafe_id=cafe_id)
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    return db_menu


@kaffe_routes.put('/menus/{menu_id}', response_model=MenuUpdate)
async def update_menu(menu_id: int, menu: MenuUpdate, db: Session = Depends(get_session)):
    db_menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not db_menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    db_menu.name = menu.name
    db.commit()
    db.refresh(db_menu)
    return db_menu


@kaffe_routes.delete('/menus/{menu_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu(menu_id: int, db: Session = Depends(get_session)):
    db_menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not db_menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menyu topilmadi")

    db.delete(db_menu)
    db.commit()
