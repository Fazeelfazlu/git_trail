from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime,Text
from repository.BaseEntity import Base


class TrainingEntity(Base):
    __tablename__ ='tblentitytraining'

    id = Column(Integer, primary_key=True)
    entitytraining_json = Column(Text, nullable=False)   
    istrained =Column(String(1), nullable=False) 
    trainingtype=Column(String(1), nullable=False) 
    modified_by = Column(String(100))
    modified_on = Column(DateTime, nullable=False)
    created_on = Column(DateTime, nullable=False)
    created_by = Column(String(100), nullable=False)
    entitites = relationship('EntityMapping',back_populates="entitytraining")