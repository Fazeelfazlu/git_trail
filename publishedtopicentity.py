from sqlalchemy import Column, Integer, String, DateTime,Text
from repository.BaseEntity import Base
from repository.policytopicassociation import PolicyTopicAssociation
from sqlalchemy.orm import relationship

class PublishedTopic(Base):
    __tablename__ ='tblpublishedtopic'

    id = Column(Integer, primary_key=True)
    project_id= Column(String(500), nullable=False)
    topic_name = Column(String(40), nullable=False)    
    created_on = Column(DateTime, nullable=False)