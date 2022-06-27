from sqlalchemy import create_engine, Column, String, Integer, Float,ForeignKey,Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:123456@192.168.184.133:3306/2202号数据库"
# app = Flask(__name__)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    encoding='utf-8',
    echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
