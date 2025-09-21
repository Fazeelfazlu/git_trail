from datetime import datetime
from repository.metapromptentity import Metaprompt
from repository.dbhandler import GetSession
from util import getCurrentDateTime
from sqlalchemy.sql import exists,and_,func
from repository.policymetapromptassociation import PolicyMetapromptAssociation

class MetapromptRepository:
    @staticmethod
    def create(metaprompt_name, metaprompt_value, metaprompt_desc, created_by):
      with GetSession() as session:
        try:        
          if MetapromptRepository.validateMetaprompt(session,metaprompt_name,0):
             return 2
          metaprompt = Metaprompt(
              metaprompt_name=metaprompt_name,
              metaprompt_value = metaprompt_value,
              metaprompt_desc=metaprompt_desc,
              modified_by=created_by,
              modified_on=getCurrentDateTime(),
              created_by=created_by,
              created_on=getCurrentDateTime()
          )
          session.add(metaprompt)
          session.commit()
          return 0
        except Exception as e:
            session.rollback()
            raise e
        finally:
           session.close()

    @staticmethod
    def read(metaprompt_id):
       with GetSession() as session:
        try:
           return session.query(Metaprompt).filter_by(id=metaprompt_id).first()
        except Exception as e:          
            raise e
        finally:
           session.close()
    
    @staticmethod
    def readall():
        with GetSession() as session:
          try:
              return session.query(Metaprompt).order_by(Metaprompt.created_on).all()
          except Exception as e:          
              raise e
          finally:
            session.close()
       

    @staticmethod
    def update(metaprompt_id, metaprompt_name, metaprompt_value,metaprompt_desc, modified_by):
      with GetSession() as session:
        try:
        
          metaprompt = session.query(Metaprompt).filter_by(id=metaprompt_id).first()
          if metaprompt:
              if MetapromptRepository.validateMetaprompt(session,metaprompt_name,metaprompt_id):
                 return 2
              metaprompt.metaprompt_name = metaprompt_name
              metaprompt.metaprompt_value = metaprompt_value
              metaprompt.metaprompt_desc=metaprompt_desc
              metaprompt.modified_by = modified_by
              metaprompt.modified_on = getCurrentDateTime()
              session.commit()
              return 0
          return 1
        except Exception as e:
          session.rollback()
          raise e
        finally:
           session.close()

    @staticmethod
    def delete(metaprompt_id):
      with GetSession() as session:
        try:
        
          metaprompt = session.query(Metaprompt).filter_by(id=metaprompt_id).first()
          if metaprompt:
              if(session.query(exists().where(PolicyMetapromptAssociation.metaprompt_id == metaprompt_id)).scalar()):
                 return 2 #indicates Foreign Key exists        
              session.delete(metaprompt)
              session.commit()
              return 0
          return 1
        except Exception as e:
          session.rollback()
          raise e
        finally:
           session.close()

    
    @staticmethod
    def validateMetaprompt(session,metapromptname,metaprompt_id):
       metapromptname=metapromptname.strip()
       return session.query(exists().where(and_(Metaprompt.id != metaprompt_id),(func.lower(Metaprompt.metaprompt_name)==func.lower(metapromptname)))).scalar()