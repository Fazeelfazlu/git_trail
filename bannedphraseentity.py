from sqlalchemy import Column, Integer, TEXT, ForeignKey
from sqlalchemy.orm import relationship
from repository.BaseEntity import Base

class BannedPhrases(Base):
    __tablename__ = 'tblbannedphrases'
    id = Column(Integer, primary_key=True)
    banned_phrase = Column(TEXT, nullable=False)
    policy_id = Column(Integer, ForeignKey('tblpolicy.id'), nullable=False)

    # Define many-to-one relationship with tblpolicy
    policy = relationship('Policy', back_populates='phrases')
