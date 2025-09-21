from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from repository.BaseEntity import Base

class PIIPolicyAssociation(Base):
    __tablename__ = 'tblpiipolicyassociation'
    id = Column(Integer, primary_key=True)
    pii_name = Column(String(100), ForeignKey('tblpii.pii_name'), nullable=False)
    policy_id = Column(Integer, ForeignKey('tblpolicy.id'), nullable=False)

    # Define many-to-one relationship with tblentity
    piientity = relationship('PIIEntity', back_populates='policies')

    # Define many-to-one relationship with tblpolicy
    policy = relationship('Policy', back_populates='piientities')
