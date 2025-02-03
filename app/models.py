from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Wallet(Base):
    __tablename__ = 'wallet'

    id = Column(String, primary_key=True)
    balance = Column(Integer, nullable=False, default=0)
