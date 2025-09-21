from sqlalchemy import Column, Integer, String, DateTime,ForeignKey,TEXT
from sqlalchemy.orm import relationship
from repository.trainingentity import TrainingEntity
from repository.BaseEntity import Base
from repository.policyentityassociation import PolicyEntityAssociation
class Entity(Base):
    __tablename__ ='tblentity'

    id = Column(Integer, primary_key=True)    
    entity_value = Column(String(40), nullable=False)    
    entity_desc=Column(TEXT, nullable=False)
    modified_by = Column(String(100), nullable=False)
    modified_on = Column(DateTime, nullable=False)
    created_on = Column(DateTime, nullable=False)
    created_by = Column(String(100), nullable=False)
    mappedtrainings = relationship('EntityMapping',back_populates="entity")
    policies = relationship("PolicyEntityAssociation",  back_populates="entity")
    prompts=relationship("Prompts",back_populates="entity")