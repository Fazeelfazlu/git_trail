from sqlalchemy import Column, String, DateTime, DECIMAL, Text
from repository.BaseEntity import Base


class TrainingStatusEntity(Base):
    __tablename__ ='tbltrainingstatus'

    training_status = Column(String(50), primary_key=True)
    modified_on = Column(DateTime, nullable=False)
    modified_by = Column(String(50), nullable=False)
    f1_score = Column(DECIMAL(10, 2))
    run_id = Column(Text)
    last_successful_training_on = Column(DateTime)
    model_source =Column(String(500), nullable=False)