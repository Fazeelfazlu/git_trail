from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from repository.BaseEntity import Base

class PolicyRegexAssociation(Base):
    __tablename__ = 'tblpolicyregexassociation'
    id = Column(Integer, primary_key=True)
    regex_id = Column(Integer, ForeignKey('tblregex.id'), nullable=False)
    policy_id = Column(Integer, ForeignKey('tblpolicy.id'), nullable=False)

    # Define many-to-one relationship with tblregex
    regex = relationship('Regex', back_populates='policies')

    # Define many-to-one relationship with tblpolicy
    policy = relationship('Policy', back_populates='regexs')
