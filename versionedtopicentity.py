from sqlalchemy import Column, Integer, String, DateTime,ForeignKey
from repository.BaseEntity import Base
from repository.policytopicassociation import PolicyTopicAssociation
from sqlalchemy.orm import relationship

class VersionedTopic(Base):
    __tablename__ ='tblversionedtopic'

    id = Column(Integer, primary_key=True)
    version_id = Column(Integer, ForeignKey('tblpublishedappversion.id'))
    project_id= Column(String(500), nullable=False)
    topic_name = Column(String(40), nullable=False)    
    created_on = Column(DateTime, nullable=False)
    version = relationship('AppVersion',back_populates="topics")