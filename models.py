from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    hash = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    boards = relationship("Board", back_populates="user")

class Board(Base):
    __tablename__ = "board"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    title = Column(String(255), nullable=False)
    description = Column(String(2048))
    creation = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    user = relationship("User", back_populates="boards")
    columns = relationship("List", back_populates="board")

class List(Base):
    __tablename__ = "list"

    id = Column(Integer, primary_key=True)
    board_id = Column(Integer, ForeignKey("board.id"))
    title = Column(String(255), nullable=False)
    description = Column(String(1024))
    creation = Column(DateTime(timezone=True), default=func.current_timestamp())
    board = relationship("Board", back_populates="columns")
    cards = relationship("Card", back_populates="list")

class Card(Base):
    __tablename__ = "card"

    id = Column(Integer, primary_key=True)
    column_id = Column(Integer, ForeignKey("list.id"))
    content = Column(String(2500), nullable=False)
    creation = Column(DateTime(timezone=True), default=func.current_timestamp())
    list = relationship("List", back_populates="cards")