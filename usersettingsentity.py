from sqlalchemy import Column, Integer, String, DateTime,Text,ForeignKey
from repository.BaseEntity import Base
from sqlalchemy.orm import relationship

class UserSettings(Base):
    __tablename__ ='tblusersettings'

    id = Column(Integer, primary_key=True)
    userid = Column(Integer, ForeignKey('tblusers.id'), nullable=False)
    setting_name = Column(String(100), nullable=False) 
    setting_value = Column(String(100), nullable=False) 
    created_on = Column(DateTime, nullable=False)
    created_by = Column(String(100), nullable=False)
    
    user = relationship('User', back_populates='settings')