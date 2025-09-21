from sqlalchemy import Column, Integer, String, DateTime,Text
from repository.BaseEntity import Base
from sqlalchemy.orm import relationship

class LLM(Base):
    __tablename__ ='tblllm'

    id = Column(Integer, primary_key=True)
    llm_family_name = Column(String(200), nullable=False)  
    llm_name   = Column(String(200), nullable=False) 
    llm_desc=Column(Text, nullable=False) 
    watermark_text= Column(Text, nullable=False)  
    license_type=Column(String(200))
    llm_url=Column(String(500))
    llm_remarks=Column(Text)
    modified_by = Column(String(100), nullable=False)
    modified_on = Column(DateTime, nullable=False)
    created_on = Column(DateTime, nullable=False)
    created_by = Column(String(100), nullable=False)

    policies = relationship("PolicyLLMAssociation", back_populates="llm")
    trainedOn = relationship("TrainedOn", back_populates="llm")