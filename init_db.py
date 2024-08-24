from database import engine, Base
from model import Cafes, User, Products, Menu

Base.metadata.create_all(bind=engine)