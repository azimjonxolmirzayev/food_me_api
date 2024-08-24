from sqlalchemy import Column, Integer, Text, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True, nullable=False)
    email = Column(String(70), unique=True, nullable=False)
    password = Column(Text, nullable=False)

    cafes = relationship("Cafes", back_populates="owner")

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"


class Cafes(Base):
    __tablename__ = "cafes"
    id = Column(Integer, primary_key=True)
    name = Column(String(25), unique=True, nullable=False)
    owner_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    location = Column(String, nullable=False)
    description = Column(String)
    phonenumber = Column(String, nullable=False)
    wifipass = Column(String)
    logo_url = Column(String)
    image_url = Column(String)

    owner = relationship("User", back_populates="cafes")
    products = relationship("Products", back_populates="cafe")
    menus = relationship("Menu", back_populates="cafe")

    def __repr__(self):
        return f"<Cafes(name={self.name}, owner_id={self.owner_id})>"


class Products(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False)
    description = Column(String(150))
    price = Column(Integer, nullable=False)
    menu_id = Column(Integer, ForeignKey('menu.id'), nullable=False)
    cafe_id = Column(Integer, ForeignKey('cafes.id'), nullable=False)
    image_url = Column(String)
    ingredients = Column(String)

    cafe = relationship("Cafes", back_populates="products")
    menu = relationship("Menu", back_populates="products")

    def __repr__(self):
        return f"<Products(name={self.name}, price={self.price})>"


class Menu(Base):
    __tablename__ = "menu"
    id = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False)
    cafe_id = Column(Integer, ForeignKey('cafes.id'), nullable=False)

    cafe = relationship("Cafes", back_populates="menus")
    products = relationship("Products", back_populates="menu")

    def __repr__(self):
        return f"<Menu(name={self.name}, cafe_id={self.cafe_id})>"