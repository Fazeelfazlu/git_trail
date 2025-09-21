from sqlalchemy import Column, Integer, String, ForeignKey
from repository.BaseEntity import Base
from sqlalchemy.orm import relationship


class PolicyGeography(Base):
    __tablename__ ='tblpolicygeography'

    id = Column(Integer, primary_key=True)
    geography = Column(String(200), nullable=False) 
    policy_id = Column(Integer, ForeignKey('tblpolicy.id'), nullable=False)
    policy=relationship('Policy',back_populates="geographies")