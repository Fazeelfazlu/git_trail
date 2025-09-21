from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from repository.BaseEntity import Base

class PolicyLLMAssociation(Base):
    __tablename__ = 'tblllmassociation'
    id = Column(Integer, primary_key=True)
    llm_id = Column(Integer, ForeignKey('tblllm.id'),nullable=False)
    policy_id = Column(Integer, ForeignKey('tblpolicy.id'), nullable=False)

    # Define many-to-one relationship with tblllm
    llm = relationship('LLM', back_populates='policies')

    # Define many-to-one relationship with tblpolicy
    policy = relationship('Policy', back_populates='llms')
