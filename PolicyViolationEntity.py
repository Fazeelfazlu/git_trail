from sqlalchemy import Column, Integer, String, DateTime,Text
from sqlalchemy.orm import relationship
from repository.BaseEntity import Base

class PolicyViolationEntity(Base):
    __tablename__ ='tblpolicyviolations'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, nullable=False)
    policy_id = Column(Integer)   
    invocation_id = Column(String(100), nullable=False)
    invocation_type=Column(String(20), nullable=False)
    violation_type=Column(String(20), nullable=False)
    violation_field_value=Column(Text)
    policy_type=Column(String(20))
    log_level=Column(String(20))
    created_on = Column(DateTime, nullable=False)
    created_by = Column(String(100), nullable=False)