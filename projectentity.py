from sqlalchemy import Column, Integer, String, DateTime,Text,ForeignKey
from repository.BaseEntity import Base
from sqlalchemy.orm import relationship


class Project(Base):
    __tablename__ ='tblproject'

    id = Column(Integer, primary_key=True)
    project_name = Column(String(100), nullable=False)
    project_desc  = Column(Text, nullable=False)
    appgroup_id=Column(Integer, ForeignKey('tblappgroup.id'), nullable=False) 
    app_ci=Column(String(100), nullable=False)
    app_url=Column(String(500))     
    owner_name=Column(String(500))
    owner_handle=Column(String(100))
    owner_email=Column(String(200))
    approver_name=Column(String(500))
    approver_handle=Column(String(100))
    approver_email=Column(String(200))
    from_date=Column(DateTime, nullable=False)
    to_date=Column(DateTime, nullable=False)
    locked=Column(String(1), nullable=False)
    active=Column(String(1), nullable=False)
    license_key=Column(Text,nullable=False)
    modified_by = Column(String(100), nullable=False)
    modified_on = Column(DateTime, nullable=False)
    created_on = Column(DateTime, nullable=False)
    created_by = Column(String(100), nullable=False)

    policies=relationship("ProjectPolicyAssociation",back_populates="project")
    appgroup=relationship("AppGroup",back_populates="projects")