from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from repository.BaseEntity import Base

class PolicyTopicAssociation(Base):
    __tablename__ = 'tblpolicytopicassociation'
    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey('tbltopic.id'), nullable=False)
    policy_id = Column(Integer, ForeignKey('tblpolicy.id'), nullable=False)

    # Define many-to-one relationship with tbltopic
    topic = relationship('Topic', back_populates='policies')

    # Define many-to-one relationship with tblpolicy
    policy = relationship('Policy', back_populates='topics')
