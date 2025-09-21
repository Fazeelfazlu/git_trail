from sqlalchemy import Column, Integer, Text, DateTime,String
from repository.BaseEntity import Base
from sqlalchemy.orm import relationship
class Metaprompt(Base):
    __tablename__ ='tblmetaprompt'

    id = Column(Integer, primary_key=True)
    metaprompt_name = Column(String(50), nullable=False)
    metaprompt_value = Column(Text, nullable=False)
    metaprompt_desc = Column(Text, nullable=False)
    modified_by = Column(String(100), nullable=False)
    modified_on = Column(DateTime, nullable=False)
    created_on = Column(DateTime, nullable=False)
    created_by = Column(String(100), nullable=False)
    policies = relationship("PolicyMetapromptAssociation",  back_populates="metaprompt")