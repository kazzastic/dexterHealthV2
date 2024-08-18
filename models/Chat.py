from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base, engine

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(String, ForeignKey('users.id'))
    receiver_id = Column(String, ForeignKey('users.id'))
    message = Column(Text, nullable=False)

Base.metadata.create_all(bind = engine)