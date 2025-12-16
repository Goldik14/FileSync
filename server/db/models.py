#server/db/models.py
from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    filename = Column(String, unique=True, nullable=False)
    hash = Column(String, nullable=False)
    size = Column(BigInteger, nullable=False)