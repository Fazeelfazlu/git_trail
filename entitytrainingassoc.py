from sqlalchemy import Column, Integer, String, DateTime,ForeignKey
from sqlalchemy.orm import relationship
from repository.trainingentity import TrainingEntity
from repository.BaseEntity import Base
from repository.policyentityassociation import PolicyEntityAssociation
class EntityMapping(Base):
    __tablename__ ='tblentitytrainingmapping'

    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey('tblentity.id'))
    entitytraining_id = Column(Integer, ForeignKey('tblentitytraining.id'))  
    entitytraining = relationship('TrainingEntity',back_populates="entitites")
    entity = relationship("Entity",  back_populates="mappedtrainings")