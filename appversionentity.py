from sqlalchemy import Column, Integer, String, DateTime,Text
from repository.BaseEntity import Base
from repository.policytopicassociation import PolicyTopicAssociation
from sqlalchemy.orm import relationship

class AppVersion(Base):
    __tablename__ ='tblpublishedappversion'

    id = Column(Integer, primary_key=True)
    project_id= Column(String(500), nullable=False)
    version_no= Column(String(10), nullable=False)   
    is_latest= Column(String(1), nullable=False)   
    created_on = Column(DateTime, nullable=False)
    created_by= Column(String(100), nullable=False)   
    versionedapp = relationship('VersionedApp',back_populates="version")
    topics=relationship('VersionedTopic',back_populates="version")