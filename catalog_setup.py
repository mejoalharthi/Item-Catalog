import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.pool import SingletonThreadPool

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'Id': self.id,
            'Name': self.name,
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    item_info = Column(String(400))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category, cascade='delete')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'Id': self.id,
            'Name': self.name,
            'inforamtion': self.item_info,
            'category_id': self.category_id,
        }


engine = create_engine('sqlite:///catalog.db?check_same_thread=False',
                       poolclass=SingletonThreadPool)
Base.metadata.create_all(engine)
