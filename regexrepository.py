from datetime import datetime
from repository.regexentity import Regex
from repository.dbhandler import GetSession
from util import getCurrentDateTime
from sqlalchemy.sql import exists,and_,func
from repository.policyregexassociation import PolicyRegexAssociation
from repository.promptrepository import PromptRepository
from sqlalchemy.orm import joinedload

class RegexRepository:
    @staticmethod
    def create(regex_name, regex_value,regex_desc,prompts,  created_by):
       with GetSession() as session:
        try:
            if RegexRepository.validateRegex(session,regex_name,0):
                return 2
            regex = Regex(
                regex_name=regex_name,
                regex_value = regex_value,
                regex_desc=regex_desc,
                modified_by=created_by,
                modified_on=getCurrentDateTime(),
                created_by=created_by,
                created_on=getCurrentDateTime()
            )
            session.add(regex)
            PromptRepository.save(session,prompts,created_by,regex=regex)
            session.commit()
            return 0
        except Exception as e:
            session.rollback()
            raise e
        finally:
           session.close()

    @staticmethod
    def read(regex_id):
        with GetSession() as session:
            try:
             return session.query(Regex).options(joinedload(Regex.prompts)).filter_by(id=regex_id).first()
            except Exception as e:
                raise e
            finally:
                session.close()
    
    @staticmethod
    def readall():
         with GetSession() as session:
            try:
              return session.query(Regex).options(joinedload(Regex.prompts)).order_by(Regex.created_on).all()
            except Exception as e:
                raise e
            finally:
                session.close()
       

    @staticmethod
    def update(regex_id, regex_name, regex_value,regex_desc,prompts, modified_by):
        with GetSession() as session:
            try:
            
                regex = session.query(Regex).filter_by(id=regex_id).first()
                if regex:
                    if RegexRepository.validateRegex(session,regex_name,regex_id):
                        return 2
                    regex.regex_name = regex_name
                    regex.regex_value = regex_value
                    regex.regex_desc=regex_desc
                    regex.modified_by = modified_by
                    regex.modified_on = getCurrentDateTime()
                    PromptRepository.save(session,prompts,modified_by,regex=regex)
                    session.commit()
                    return 0
                return 1
            except Exception as e:
                session.rollback()
                raise e
            finally:
               session.close()

    @staticmethod
    def delete(regex_id):
     with GetSession() as session:
        try:
            session=GetSession()
            regex = session.query(Regex).filter_by(id=regex_id).first()
            if regex:
                if(session.query(exists().where(PolicyRegexAssociation.regex_id == regex_id)).scalar()):
                     return 2 #indicates Foreign Key exists   
                PromptRepository.delete (session,regex_id=regex_id)              
                session.delete(regex)
                session.commit()
                return 0
            return 1
        except Exception as e:
            session.rollback()
            raise e
        finally:
           session.close()


    @staticmethod
    def validateRegex(session,regex_name,regex_id):
       regex_name=regex_name.strip()
       return session.query(exists().where(and_(Regex.id != regex_id),(func.lower(Regex.regex_name)==func.lower(regex_name)))).scalar()