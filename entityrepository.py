from repository.trainingentity import TrainingEntity
from repository.customentity import Entity
import logging
from util import getCurrentDateTime
from repository.dbhandler import GetSession
import json
from logger import logger
from sqlalchemy.orm import joinedload
from sqlalchemy import and_,exists,func
from repository.policyentityassociation import PolicyEntityAssociation
from repository.trainingstatusrepository import TrainingStatusRepository
from repository.entitytrainingassoc import EntityMapping
from datareader import readfileAndGetData
from repository.promptrepository import PromptRepository
from sqlalchemy import and_
class EntityRepository:
    @staticmethod
    def create(entitytraining_json, created_by):
        trainingtype=entitytraining_json.type
        entitytraining_json = entitytraining_json.__dict__
        del entitytraining_json["type"]
        entitytraining_json=json.dumps(entitytraining_json)
        with GetSession() as session:
            try:
               
                trainigingentity = TrainingEntity(
                    entitytraining_json=entitytraining_json,
                    istrained="N",
                    trainingtype=trainingtype,
                    modified_by=created_by,
                    modified_on=getCurrentDateTime(),
                    created_by=created_by,
                    created_on=getCurrentDateTime()
                )
                jsondata=json.loads(entitytraining_json)            
                classes=jsondata["classes"]
                trainigingentity = EntityRepository.saveEntities(classes,session,trainigingentity,created_by)
                session.add(trainigingentity) 
                constants = readfileAndGetData('constants')
                status=constants["MODEL_TRAIN_STATUS"]["MODEL_OUTDATED"]
                TrainingStatusRepository.updatetrainingstatus(session,status,created_by)
                session.commit()
                return trainigingentity
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
    
    @staticmethod
    def saveEntities(classes,session,trainigingentity,created_by):
        for entname in classes:
            entityobj=session.query(Entity).filter_by(entity_value=entname).first()
            if entityobj:
                entitymapping=EntityMapping(
                    entity_id=entityobj.id
                )           
                trainigingentity.entitites.append(entitymapping)     
            else:
                entity=Entity(                      
                        entity_value=entname,
                        modified_by=created_by,
                        modified_on=getCurrentDateTime(),
                        created_by=created_by,
                        created_on=getCurrentDateTime(),
                        entity_desc=" "
                    )
                entitymapping=EntityMapping(
                   entity=entity
                )
                trainigingentity.entitites.append(entitymapping)
        existids=session.query(EntityMapping.entity_id)
        policymappedentities=session.query(PolicyEntityAssociation.entity_id)
        delentities=session.query(Entity).filter(and_(Entity.id.not_in(existids)),(Entity.id.not_in(policymappedentities)))
        for delentity in delentities:
            PromptRepository.delete(session,entity_id=delentity.id)
            session.delete(delentity)      
        return trainigingentity     

    @staticmethod
    def read(entity_training_id):
       with GetSession() as session:
        try:
            return session.query(TrainingEntity).filter_by(id=entity_training_id).first()
        except Exception as e:
            raise e
        finally:
             session.close()

    @staticmethod
    def readall():
        with GetSession() as session:
            try:
                return session.query(TrainingEntity).options(joinedload(TrainingEntity.entitites).subqueryload(EntityMapping.entity)).order_by(TrainingEntity.created_on).all()
            except Exception as e:
                raise e
            finally:
                session.close()
    
    @staticmethod
    def readallEntity():
        with GetSession() as session:
            try:
                return session.query(Entity).options(joinedload(Entity.prompts)).order_by(Entity.created_on).all()
            except Exception as e:
                raise e
            finally:
                session.close()
       

    @staticmethod
    def update(entitytraining_json, id, modified_by):
      with GetSession() as session:
        try:
            trainingtype=entitytraining_json.type
            entitytraining_json = entitytraining_json.__dict__
            del entitytraining_json["type"]
            entitytraining_json=json.dumps(entitytraining_json)
            entitytraining = session.query(TrainingEntity).filter_by(id=id).first()
            if entitytraining:
                entitytraining.entitytraining_json = entitytraining_json
                entitytraining.trainingtype=trainingtype,
                entitytraining.istrained="N"
                entitytraining.modified_by = modified_by
                entitytraining.modified_on = getCurrentDateTime()
                jsondata=json.loads(entitytraining_json)
                classes=jsondata["classes"]
                session.query(EntityMapping).filter_by(
                    entitytraining_id=id).delete()
                entitytraining=EntityRepository.saveEntities(classes,session,entitytraining,modified_by)
                constants = readfileAndGetData('constants')
                status=constants["MODEL_TRAIN_STATUS"]["MODEL_OUTDATED"]
                TrainingStatusRepository.updatetrainingstatus(session,status,modified_by)    
                session.commit()
                return entitytraining        
            return None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
      
    @staticmethod
    def readalltraining(trainingtype):
         with GetSession() as session:
            try:
                  return session.query(TrainingEntity).filter_by(trainingtype=trainingtype).order_by(TrainingEntity.created_on)    
            except Exception as e:
                raise e
            finally:
                session.close()     
      
        # written to update istrained property from "N" to "Y" after training 
    
    @staticmethod
    def updatetrainedentities(trainingtype):
        with GetSession() as session:
            try:
                # Define the filters
                istrainedfilter = TrainingEntity.istrained == "N"
                trainingtypefilter = TrainingEntity.trainingtype == trainingtype
                combined_filter = and_(istrainedfilter, trainingtypefilter)

                untrainedentities = session.query(TrainingEntity).filter_by(combined_filter).all()  

                for entity in untrainedentities:
                    entity.istrained = 'Y'
                    #entity.modified_on = getCurrentDateTime()
                    session.commit()
            except Exception as e:
                raise e
            finally:
                session.close()                    


    @staticmethod
    def updateEntityDetails(entity_id,entity_obj,updated_by):
         with GetSession() as session:
            try:
                entity=session.query(Entity).filter_by(id=entity_id).first() 
                if entity:
                    entity.entity_desc=entity_obj.entity_desc
                    PromptRepository.save(session,entity_obj.prompts,updated_by,entity=entity)
                    session.commit()
                    return 0
                else:
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
                trainingentity=session.query(TrainingEntity).filter_by(id=id).first() 
                if trainingentity:
                   
                    session.query(EntityMapping).filter_by(entitytraining_id=id).delete()
                    session.delete(trainingentity)
                    EntityRepository.checkanddeleteorphanentity(session)
                    session.commit()
                    return 0
                else:
                    return 1
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()   

    @staticmethod
    def checkanddeleteorphanentity(session):
        existids=session.query(EntityMapping.entity_id)
        policymappedentities=session.query(PolicyEntityAssociation.entity_id)
        delentities=session.query(Entity).filter(and_(Entity.id.not_in(existids)),(Entity.id.not_in(policymappedentities)))
        for delentity in delentities:
            PromptRepository.delete(session,entity_id=delentity.id)
            session.delete(delentity)


    @staticmethod
    def UpdateTrainingCompleted():
         with GetSession() as session:
            try:
                session.query(TrainingEntity).update({TrainingEntity.istrained:"Y"})
                session.commit()
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()  
"""
# Example usage:
if __name__ == "__main__":
    
    # Create a new topic
    new_topic = TopicRepository.create("New Topic", "Admin", "Admin")
    
    # Read the topic
    topic_read = TopicRepository.read(new_topic.id)

    # Update the topic
    updated_topic = TopicRepository.update(new_topic.id, "Updated Topic", "Admin")
    
    # Delete the topic
    deleted = TopicRepository.delete(new_topic.id)
"""
