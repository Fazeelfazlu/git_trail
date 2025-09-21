from sqlalchemy import Column, Integer, String, DateTime,Text
from repository.BaseEntity import Base
from sqlalchemy.orm import relationship


class Regex(Base):
    __tablename__ ='tblregex'

    id = Column(Integer, primary_key=True)
    regex_name = Column(String(50), nullable=False)
    regex_value = Column(String(200), nullable=False)
    regex_desc=Column(Text, nullable=False)
    modified_by = Column(String(100), nullable=False)
    modified_on = Column(DateTime, nullable=False)
    created_on = Column(DateTime, nullable=False)
    created_by = Column(String(100), nullable=False)
    policies = relationship("PolicyRegexAssociation",  back_populates="regex")
    prompts=relationship("Prompts",back_populates="regex")
    