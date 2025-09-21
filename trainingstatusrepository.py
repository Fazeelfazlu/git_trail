from sqlalchemy.orm import Session
from repository.BaseEntity import Base
from repository.dbhandler import GetSession
from util import getCurrentDateTime,getUTCDateAndTimefromLocalDate
from datareader import readfileAndGetData
from repository.trainingstatusentity import TrainingStatusEntity
from logger import logger
constants = readfileAndGetData('constants')

class TrainingStatusRepository:
    @staticmethod
    def update(trainingstatusentity):
        with GetSession() as session:
            try:
                TrainingStatusRepository.updatetraining(session,trainingstatusentity)
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()

    @staticmethod
    def updatetraining(session,trainingstatusentity):
            trainingstatusobj = session.query(TrainingStatusEntity).first()
            if trainingstatusobj:
                trainingstatusobj.training_status = trainingstatusentity.training_status
                trainingstatusobj.modified_on = getCurrentDateTime()
                trainingstatusobj.modified_by = trainingstatusentity.modified_by
                trainingstatusobj.f1_score = trainingstatusentity.f1_score
                trainingstatusobj.run_id = trainingstatusentity.run_id
                trainingstatusobj.model_source="Trained-In Situ"
                trainingstatusobj.last_successful_training_on = getCurrentDateTime() if trainingstatusentity.training_status == constants['MODEL_TRAIN_STATUS']['TRAIN_SUCCESS'] else trainingstatusobj.last_successful_training_on       
                session.commit()
                return 0
            return 1
    
    @staticmethod
    def updatetrainingstatus(session,status,modifiedby):
            trainingstatusobj = session.query(TrainingStatusEntity).first()
            if trainingstatusobj:
                trainingstatusobj.training_status = status
                trainingstatusobj.modified_on = getCurrentDateTime()
                trainingstatusobj.modified_by =modifiedby               
                session.commit()
                return 0
            return 1


    @staticmethod
    def initiatetraining(username):
         with GetSession() as session:
            try:
                trainingstatusobj = session.query(TrainingStatusEntity).first()
                if trainingstatusobj:
                    trainingstatusobj.training_status = constants['MODEL_TRAIN_STATUS']['TRAIN_INIT']
                    trainingstatusobj.modified_on = getCurrentDateTime()
                    trainingstatusobj.modified_by = username
                    session.commit()
                    return 0
                return 1
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()

    @staticmethod
    def getlateststatus():
        with GetSession() as session:
            try:
                return session.query(TrainingStatusEntity).first().training_status
            except Exception as e:
                raise e
            finally:
                session.close()
                
    @staticmethod
    def gettriggeredbyuser():
        with GetSession() as session:
            try:
                return session.query(TrainingStatusEntity).first().modified_by
            except Exception as e:
                raise e
            finally:
                session.close()

    @staticmethod
    def GetEntityStatus():
        with GetSession() as session:
            try:
                    return session.query(TrainingStatusEntity).first()
            except Exception as e:
                    raise e
            finally:
                session.close()

    @staticmethod
    def updatetrainingprogress():
        with GetSession() as session:
            try:
                trainingstatusobj = session.query(TrainingStatusEntity).first()
                if trainingstatusobj:
                    trainingstatusobj.training_status = constants['MODEL_TRAIN_STATUS']['TRAIN_PROGRESS']
                    trainingstatusobj.modified_on = getCurrentDateTime()                    
                    session.commit()
                    return 0
                return 1
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()

    @staticmethod
    def ImportModelData(trainingData):
         with GetSession() as session:
            try:
                trainingstatusobj = session.query(TrainingStatusEntity).first()
                if trainingstatusobj:
                    score=trainingData['score']/100 if trainingData['score'] else 0 
                    run_date=getUTCDateAndTimefromLocalDate(trainingData['run_date'])
                    logger.info(f"Object-{trainingData['run_date']},Converted - {run_date}")                
                    trainingstatusobj.training_status = constants['MODEL_TRAIN_STATUS']['TRAIN_SUCCESS']
                    trainingstatusobj.modified_on = getCurrentDateTime()  
                    trainingstatusobj.f1_score = score
                    trainingstatusobj.last_successful_training_on =run_date
                    #trainingstatusobj.last_successful_training_on =getCurrentDateTime()
                    trainingstatusobj.model_source=f"Imported from {trainingData['env']}"                  
                    session.commit()
                    return 0
                return 1
            except Exception as e:
                logger.error(f"Error occured in Updating Status {e}")
                session.rollback()
                raise e
            finally:
                session.close()