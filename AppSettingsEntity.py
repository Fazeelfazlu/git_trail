from sqlalchemy import Column, Integer, String, DateTime,Text
from repository.BaseEntity import Base
from sqlalchemy.orm import relationship


class AppSettings(Base):
    __tablename__ ='tblappsettings'


    setting_name = Column(String(100), primary_key=True) 
    setting_value=   Column(Text, nullable=False)