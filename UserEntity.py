from sqlalchemy import Column, Integer, String, DateTime,Text
from repository.BaseEntity import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ ='tblusers'

    id = Column(Integer, primary_key=True)
    username = Column(String(300), nullable=False)  
    firstname = Column(String(100), nullable=False)    
    lastname = Column(String(100), nullable=False)    
    password=Column(String(200), nullable=False)
    user_role=Column(String(50), nullable=False)
    active=Column(String(1), nullable=False)
    locked=Column(String(1), nullable=False)
    incorrect_attempt=Column(Integer)
    lastlogintime=Column(DateTime)
    lockeddatetime=Column(DateTime)
    is_two_factor_enabled=Column(String(1), nullable=False)
    is_two_factor_required=Column(String(1), nullable=False)
    secret_token=Column(Text, nullable=False)
    modified_by = Column(String(100), nullable=False)
    modified_on = Column(DateTime, nullable=False)
    created_on = Column(DateTime, nullable=False)
    created_by = Column(String(100), nullable=False)
    required_pwd_change=Column(String(1), nullable=False)
    
    eventlogs=relationship("UserEventLog",back_populates="user")
    settings=relationship("UserSettings",back_populates="user")