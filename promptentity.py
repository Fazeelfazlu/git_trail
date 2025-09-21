from sqlalchemy import Column, Integer, Text,DateTime,ForeignKey,String
from repository.BaseEntity import Base
from sqlalchemy.orm import relationship


class Prompts(Base):
    __tablename__ ='tblprompts'

    id = Column(Integer, primary_key=True)
    prompt=Column(Text,nullable=False)
    topic_id = Column(Integer, ForeignKey('tbltopic.id'))
    regex_id = Column(Integer, ForeignKey('tblregex.id'))
    entity_id = Column(Integer, ForeignKey('tblentity.id'))  
    policy_id = Column(Integer, ForeignKey('tblpolicy.id'))    
    modified_by = Column(String(100), nullable=False)
    modified_on = Column(DateTime, nullable=False)
    created_on = Column(DateTime, nullable=False)
    created_by = Column(String(100), nullable=False)
    topic = relationship("Topic",  back_populates="prompts")
    regex = relationship("Regex",  back_populates="prompts")
    entity=relationship("Entity",  back_populates="prompts")
    policy=relationship("Policy",  back_populates="prompts")