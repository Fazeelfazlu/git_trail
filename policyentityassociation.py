from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from repository.BaseEntity import Base

class PolicyEntityAssociation(Base):
    __tablename__ = 'tblpolicyentityassociation'
    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey('tblentity.id'), nullable=False)
    policy_id = Column(Integer, ForeignKey('tblpolicy.id'), nullable=False)

    # Define many-to-one relationship with tblentity
    entity = relationship('Entity', back_populates='policies')

    # Define many-to-one relationship with tblpolicy
    policy = relationship('Policy', back_populates='entities')
