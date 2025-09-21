from sqlalchemy import Column, Integer, String, DateTime,Text,ForeignKey
from repository.BaseEntity import Base
from sqlalchemy.orm import relationship

class AdminEventLog(Base):
    
    __tablename__ ='tbladmineventlog'

    id = Column(Integer, primary_key=True)
    eventname = Column(String(100), nullable=False) 
    project_id = Column(String(500)) 
    prev_value = Column(Text)
    new_value = Column(Text, nullable=False)
    created_on = Column(DateTime, nullable=False)
    created_by = Column(String(100), nullable=False)
    
 