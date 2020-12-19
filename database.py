from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
Engine = create_engine("sqlite:///", echo=True)

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    hash = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    email = Column(String, nullable=False)
    creation = Column(DateTime, nullable=False, deault=func.)

class Posts(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    content = Column(String(255), nullable=False)
    likes = Column(Integer, nullable=False, default=0)
    creation = Column(DateTime, nullable=False, default=func.now())
    user = relationship("Users", back_populates="posts")

class Comments(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    post_id = Column(Intger, ForeignKey('posts.id'))
    content = Column(String(255), nullable=False)
    likes = Column(Intger, nullable=False, default=0)
    creation = Column(DateTime, nullable=False, default=func.now())
    post = relationship("Posts", back_populates="comments")

Users.posts = relationship("Posts", order_by=Posts.id, back_populates="user")
Posts.comments = relationship("Comments", order_by=Comments.id, back_populates="post")
Base.metadata.create_all(Engine)