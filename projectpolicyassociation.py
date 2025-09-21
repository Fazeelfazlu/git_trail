from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from repository.BaseEntity import Base

class ProjectPolicyAssociation(Base):
    __tablename__ = 'tblprojectpolicyassociation'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('tblproject.id'), nullable=False)
    policy_id = Column(Integer, ForeignKey('tblpolicy.id'), nullable=False)

    # Define many-to-one relationship with tblproject
    project = relationship('Project', back_populates='policies')

    # Define many-to-one relationship with tblpolicy
    policy = relationship('Policy', back_populates='projects')