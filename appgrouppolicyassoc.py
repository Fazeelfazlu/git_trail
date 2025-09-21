from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from repository.BaseEntity import Base

class AppGroupAssociation(Base):
    __tablename__ = 'tblappgrouppolicyassociation'
    id = Column(Integer, primary_key=True)
    appgroup_id = Column(Integer, ForeignKey('tblappgroup.id'), nullable=False)
    policy_id = Column(Integer, ForeignKey('tblpolicy.id'), nullable=False)

    # Define many-to-one relationship with tblproject
    appgroup = relationship('AppGroup', back_populates='policies')

    # Define many-to-one relationship with tblpolicy
    policy = relationship('Policy', back_populates='appgroups')