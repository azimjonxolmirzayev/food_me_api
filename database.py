from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine('postgresql://foodme_db_owner:QSqEusP0X4BF@ep-super-snow-a2dvdxcb.eu-central-1.aws.neon.tech/foodme_db?sslmode=require',
                       echo=True)

Base = declarative_base()
session = sessionmaker()
