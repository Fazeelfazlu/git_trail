from sqlalchemy import Column, Integer, String, DateTime,Text,ForeignKey
from repository.BaseEntity import Base
from sqlalchemy.orm import relationship

class TrainedOn(Base):
    __tablename__ ='tbltrainedon'

    id = Column(Integer, primary_key=True)
    datasetname = Column(String(200), nullable=False)  
    data_url=Column(String(500))
    version   = Column(String(50)) 
    remarks=Column(Text)
    llm_id = Column(Integer, ForeignKey('tblllm.id'))
    modified_by = Column(String(100), nullable=False)
    modified_on = Column(DateTime, nullable=False)
    created_on = Column(DateTime, nullable=False)
    created_by = Column(String(100), nullable=False)

    llm = relationship("LLM", back_populates="trainedOn")