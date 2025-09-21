from repository.topicentity import Topic
import logging
from util import getCurrentDateTime
from repository.dbhandler import GetSession
from sqlalchemy.sql import exists,and_,func
from repository.policytopicassociation import PolicyTopicAssociation
from repository.promptrepository import PromptRepository
from sqlalchemy.orm import joinedload

class TopicRepository:
    @staticmethod
    def create(topic_name,topic_desc,prompts, created_by):
      with GetSession() as session:
        try:    
          if(TopicRepository.validateTopic(session,topic_name,0)):
             return 2
          topic = Topic(
              topic_name=topic_name,
              topic_desc=topic_desc,
              modified_by=created_by,
              modified_on=getCurrentDateTime(),
              created_by=created_by,
              created_on=getCurrentDateTime()
          )
          session.add(topic)
          PromptRepository.save(session,prompts,created_by,topic=topic)
          session.commit()
          return 0
        except Exception as e:
            session.rollback()
            raise e
        finally:
           session.close()

    @staticmethod
    def read(topic_name):
         with GetSession() as session:
            try:  
              return session.query(Topic).options(joinedload(Topic.prompts)).filter_by(name=topic_name).first()
            except Exception as e:
                raise e
            finally:
               session.close()
    
    @staticmethod
    def readall():
         with GetSession() as session:
            try:  
               return session.query(Topic).options(joinedload(Topic.prompts)).order_by(Topic.created_on).all()
            except Exception as e:
                raise e
            finally:
               session.close()

    @staticmethod
    def readalltopics(session):
        return session.query(Topic).all()
       

    @staticmethod
    def update( new_topic_name,new_topic_desc,prompts, id, modified_by):
      with GetSession() as session:
        try:       
          topic = session.query(Topic).filter_by(id=id).first()
          if topic:
              if(TopicRepository.validateTopic(session,new_topic_name,id)):
                  return 2
              topic.topic_name = new_topic_name
              topic.topic_desc=new_topic_desc
              topic.modified_by = modified_by
              topic.modified_on = getCurrentDateTime()
              PromptRepository.save(session,prompts,modified_by,topic=topic)
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
          
          topic = session.query(Topic).filter_by(id=id).first()
          if topic:
              if(session.query(exists().where(PolicyTopicAssociation.topic_id == id)).scalar()):
                 return 2 #indicates Foreign Key exists 
              PromptRepository.delete (session,topic_id=id)          
              session.delete(topic)
              session.commit()
              return 0
          return 1 # indicates Record not found
        except Exception as e:
          session.rollback()
          raise e
        finally:
           session.close()


    @staticmethod
    def validateTopic(session,topic_name,topic_id):
       topic_name=topic_name.strip()
       return session.query(exists().where(and_(Topic.id != topic_id),(func.lower(Topic.topic_name)==func.lower(topic_name)))).scalar()