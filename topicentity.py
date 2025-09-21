from sqlalchemy import Column, Integer, String, DateTime,Text
from repository.BaseEntity import Base
from repository.policytopicassociation import PolicyTopicAssociation
from sqlalchemy.orm import relationship

class Topic(Base):
    __tablename__ ='tbltopic'

    id = Column(Integer, primary_key=True)
    topic_name = Column(String(40), nullable=False) 
    topic_desc =Column(Text, nullable=False)
    modified_by = Column(String(100), nullable=False)
    modified_on = Column(DateTime, nullable=False)
    created_on = Column(DateTime, nullable=False)
    created_by = Column(String(100), nullable=False)

    policies = relationship("PolicyTopicAssociation", back_populates="topic")
    prompts=relationship("Prompts",back_populates="topic")