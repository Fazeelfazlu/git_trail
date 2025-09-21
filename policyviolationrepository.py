from repository.PolicyViolationEntity import PolicyViolationEntity
import logging
from util import getCurrentDateTime,getUTCDatefromLocalDate
from repository.dbhandler import GetSession
from sqlalchemy import func,or_,distinct
from datetime import datetime, timedelta
from create_app import app,config_data
from datareader import readfileAndGetData

class PolicyViolationRepository:
    @staticmethod
    def create(policyviolationlist):
      with GetSession() as session:
        try:         
         for policyviolation in policyviolationlist:            
            session.add(policyviolation)
         session.commit()
         return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
           session.close()
    
    @staticmethod
    def readviolations(project_id,policy_id,startdate,enddate):
        with GetSession() as session:
          try:  
              startdate=getUTCDatefromLocalDate(startdate)
              enddate=getUTCDatefromLocalDate(enddate)
              #project_id=int(project_id)
              policy_id=int(policy_id)
              query = session.query(PolicyViolationEntity)
              query=query.filter(
               PolicyViolationEntity.created_on>=startdate,
               PolicyViolationEntity.created_on<=enddate
              )
              if not project_id=="0":
                query=query.filter_by(project_id=project_id)
              if not policy_id==0:
                query=query.filter_by(policy_id=policy_id)
              return query.order_by(PolicyViolationEntity.created_on).all()
          except Exception as e:
              raise e
          finally:
              session.close()


    @staticmethod
    def CheckPerUserViolation(username,proj_id):
       currentDate=getCurrentDateTime()
       lockoutduration=config_data['LOCKOUT_TIME']
       starttime=currentDate - timedelta(hours=0, minutes=lockoutduration)
       with GetSession() as session:
          try:  
            constants= readfileAndGetData("constants") 
            query = session.query(PolicyViolationEntity).with_entities(func.count(distinct(PolicyViolationEntity.invocation_id)))
            query=query.filter(PolicyViolationEntity.created_by==username,PolicyViolationEntity.invocation_type==constants["INVOCATION_TYPE"]["REQ"],PolicyViolationEntity.project_id==proj_id)
            query=query.filter(or_ (PolicyViolationEntity.policy_type==constants["POLICY_TYPE"]["BLOCK"],PolicyViolationEntity.policy_type==None))
            return query.filter(
                    PolicyViolationEntity.created_on>=starttime,
                    PolicyViolationEntity.created_on<=currentDate
                    ).first()[0]
          except Exception as e:
              raise e
          finally:
              session.close()
            
            
            
            
          

