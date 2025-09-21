from sqlalchemy import Column, Integer, String, DateTime,DECIMAL,Text
from repository.BaseEntity import Base
from sqlalchemy.orm import relationship


class Policy(Base):
    __tablename__ ='tblpolicy'

    id = Column(Integer, primary_key=True)
    policy_name = Column(String(100), nullable=False)   
    policy_desc= Column(Text, nullable=False)   
    industry=Column(String(100), nullable=False)   
    log_level=Column(String(50), nullable=False)
    code_checker=Column(String(1), nullable=False)
    anonymize=Column(String(1), nullable=False)
    block_pii=Column(String(1), nullable=False)
    policy_type=Column(String(20), nullable=False)
    injectionthreshold=Column(DECIMAL(3, 2), nullable=False)
    hatefulsentimentthreshold=Column(DECIMAL(3, 2), nullable=False)
    toxicitythreshold=Column(DECIMAL(3, 2), nullable=False)
    modified_by = Column(String(100), nullable=False)
    modified_on = Column(DateTime, nullable=False)
    created_on = Column(DateTime, nullable=False)
    created_by = Column(String(100), nullable=False)

    entities=relationship("PolicyEntityAssociation",back_populates="policy")
    topics = relationship("PolicyTopicAssociation", back_populates="policy")
    regexs = relationship("PolicyRegexAssociation", back_populates="policy")
    metaprompts = relationship("PolicyMetapromptAssociation", back_populates="policy")
    projects= relationship("ProjectPolicyAssociation", back_populates="policy")
    llms= relationship("PolicyLLMAssociation", back_populates="policy")
    piientities= relationship("PIIPolicyAssociation", back_populates="policy")
    phrases= relationship("BannedPhrases", back_populates="policy")
    appgroups= relationship("AppGroupAssociation", back_populates="policy")
    prompts=relationship("Prompts",back_populates="policy")
    geographies=relationship("PolicyGeography",back_populates="policy")