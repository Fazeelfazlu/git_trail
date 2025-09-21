from sqlalchemy import Column, Integer, String, ForeignKey
from repository.BaseEntity import Base
from sqlalchemy.orm import relationship

class PIIGroup(Base):
    __tablename__ ='tblpiigroups'

    group_name = Column(String(50), primary_key=True)
    group_desc = Column(String(200), nullable=False)
    piientities = relationship('PIIEntity',back_populates="piigroup")

class PIIEntity(Base):
    __tablename__ ='tblpii'

    pii_name = Column(String(100), primary_key=True)
    pii_desc = Column(String(200), nullable=False)
    group_name = Column(String(50), ForeignKey('tblpiigroups.group_name'))
    piigroup = relationship('PIIGroup',back_populates="piientities")
    policies=relationship('PIIPolicyAssociation',back_populates="piientity")
