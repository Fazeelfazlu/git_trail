from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from repository.BaseEntity import Base

class PolicyMetapromptAssociation(Base):
    __tablename__ = 'tblpolicymetapromptassociation'
    id = Column(Integer, primary_key=True)
    metaprompt_id = Column(Integer, ForeignKey('tblmetaprompt.id'), nullable=False)
    policy_id = Column(Integer, ForeignKey('tblpolicy.id'), nullable=False)

    # Define many-to-one relationship with tblmetaprompt
    metaprompt = relationship('Metaprompt', back_populates='policies')

    # Define many-to-one relationship with tblpolicy
    policy = relationship('Policy', back_populates='metaprompts')
