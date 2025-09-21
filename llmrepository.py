from repository.llmentity import LLM
from repository.trainedonentity import TrainedOn
import logging
from util import getCurrentDateTime
from repository.dbhandler import GetSession
from sqlalchemy.sql import exists, and_,func
from repository.policyllmassociation import PolicyLLMAssociation
from sqlalchemy.orm import joinedload
from logger import logger

class LLMRepository:
    @staticmethod
    def create(llmobj, created_by):
      with GetSession() as session:
        try:      
          if LLMRepository.validateLLM(session,llmobj.name,0) :
             return 2
          llm = LLM(
              llm_name=llmobj.name,
              llm_family_name=llmobj.family_name,
              watermark_text=llmobj.watermark_text,
              llm_remarks=llmobj.llm_remarks,
              llm_url=llmobj.llm_url,
              license_type=llmobj.license_type,
              llm_desc=llmobj.llm_desc,
              modified_by=created_by,
              modified_on=getCurrentDateTime(),
              created_by=created_by,
              created_on=getCurrentDateTime()
          )
          for trainedOn in llmobj.trainedOn:
             trainedEntity=TrainedOn(
                datasetname=trainedOn.datasetname,
                data_url=trainedOn.data_url,
                version=trainedOn.version,
                remarks=trainedOn.remarks,
                modified_by=created_by,
                modified_on=getCurrentDateTime(),
                created_by=created_by,
                created_on=getCurrentDateTime()
               )
             llm.trainedOn.append(trainedEntity)
          session.add(llm)
          session.commit()
          return 0
        except Exception as e:
            session.rollback()
            raise e
        finally:
           session.close()

    @staticmethod
    def read(llm_name):
        with GetSession() as session:
           try:
              return session.query(LLM).filter_by(llm_name=llm_name).first()
           except Exception as e:
              raise e
           finally:
              session.close()
    
    @staticmethod
    def readall():
        with GetSession() as session:
           try:
              return session.query(LLM).options(joinedload(LLM.trainedOn)).order_by(LLM.created_on).all()
           except Exception as e:
              raise e
           finally:
              session.close()
        

    @staticmethod
    def update( llmobj, id, modified_by):
      with GetSession() as session:
        try:       
          llm = session.query(LLM).filter_by(id=id).first()
          if llm:
              if LLMRepository.validateLLM(session,llmobj.name,id) :
                return 2
              llm.llm_family_name = llmobj.family_name
              llm.watermark_text=llmobj.watermark_text
              llm.llm_name = llmobj.name
              llm.llm_remarks=llmobj.llm_remarks,
              llm.llm_url=llmobj.llm_url,
              llm.license_type=llmobj.license_type,
              llm.llm_desc=llmobj.llm_desc,
              llm.modified_by = modified_by
              llm.modified_on = getCurrentDateTime()
              allrelatedTrainedOn=llm.trainedOn
              logger.info("----------after llm",llm)
              for trainedOnEntity in allrelatedTrainedOn:
                 if len([data for data in llmobj.trainedOn if data.id==trainedOnEntity.id])==0:
                     deletedTrainedEntity=session.query(TrainedOn).filter_by(id=trainedOnEntity.id).first()
                     session.delete(deletedTrainedEntity)

              for trainedOn in llmobj.trainedOn:
                  if not trainedOn.id or trainedOn.id==0:
                     trainedEntity=TrainedOn(
                        datasetname=trainedOn.datasetname,
                        data_url=trainedOn.data_url,
                        version=trainedOn.version,
                        remarks=trainedOn.remarks,
                        modified_by=modified_by,
                        modified_on=getCurrentDateTime(),
                        created_by=modified_by,
                        created_on=getCurrentDateTime()
                     )
                     llm.trainedOn.append(trainedEntity)
                  else:
                      trainedOnData = session.query(TrainedOn).filter_by(id=trainedOn.id).first()
                      trainedOnData.datasetname=trainedOn.datasetname
                      trainedOnData.data_url=trainedOn.data_url
                      trainedOnData.version=trainedOn.version
                      trainedOnData.remarks=trainedOn.remarks
                      trainedOnData.modified_by=modified_by
                      trainedOnData. modified_on=getCurrentDateTime()
               
              session.commit()
              return 0
          return 1
        except Exception as e:
          session.rollback()
          raise e
        finally:
           session.close()

    @staticmethod
    def delete(id):
      with GetSession() as session:
        try:        
          llm = session.query(LLM).filter_by(id=id).first()
          if llm:
              if(session.query(exists().where(PolicyLLMAssociation.llm_id == id)).scalar()):
                 return 2 #indicates Foreign Key exists  
              session.query(TrainedOn).filter_by(llm_id=id).delete()
              session.delete(llm)
              session.commit()
              return 0
          return 1
        except Exception as e:
          session.rollback()
          raise e
        finally:
           session.close()

    @staticmethod
    def validateLLM(session,llm_name,llm_id):
       llm_name=llm_name.strip()
       return session.query(exists().where(and_(LLM.id != llm_id),(func.lower(LLM.llm_name)==func.lower(llm_name)))).scalar()
