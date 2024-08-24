from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from auth_routes import auth_router
from order_routes import order_router
from fastapi_jwt_auth import AuthJWT
from schemas import Settings, LoginModel
from kaffe_routes import kaffe_routes


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://food-me-psi.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@AuthJWT.load_config
def get_config():
    return Settings()


app.include_router(auth_router)
app.include_router(order_router)
app.include_router(kaffe_routes)


@app.get('/')
async def root():
    return {'message': "Fast api loyiha ishladi"}
