from sqlalchemy import Column, String
import uuid
from database import Base, engine

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key = True, default = lambda: str(uuid.uuid4()))
    username = Column(String, unique = True, nullable = False)
    password = Column(String, nullable = False)

Base.metadata.create_all(bind = engine)