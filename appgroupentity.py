from sqlalchemy import Column, Integer, String, DateTime,Text
from repository.BaseEntity import Base
from sqlalchemy.orm import relationship


class AppGroup(Base):
    __tablename__ ='tblappgroup'

    id = Column(Integer, primary_key=True)
    group_name = Column(String(100), nullable=False) 
    group_desc=   Column(Text, nullable=False) 
    modified_by = Column(String(100), nullable=False)
    modified_on = Column(DateTime, nullable=False)
    created_on = Column(DateTime, nullable=False)
    created_by = Column(String(100), nullable=False)

    policies=relationship("AppGroupAssociation",back_populates="appgroup")
    projects=relationship("Project",back_populates="appgroup")