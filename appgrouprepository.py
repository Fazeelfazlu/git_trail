import logging
import uuid
from repository.dbhandler import GetSession
from util import getCurrentDateTime
from repository.appgrouppolicyassoc import AppGroupAssociation
from repository.appgroupentity import AppGroup
from repository.projectentity import Project
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import and_,exists,func

class AppgroupRepository:
    @staticmethod
    def create(appgroup_obj, modified_by):
        with GetSession() as session:
            try:
                if AppgroupRepository.validateAppGroup(session,appgroup_obj.name,0):
                    return 2
                appgroup = AppGroup(
                    group_name=appgroup_obj.name,
                    group_desc=appgroup_obj.desc,
                    modified_by=modified_by,
                    modified_on=getCurrentDateTime(),
                    created_by=modified_by,
                    created_on=getCurrentDateTime()
                )
                session.add(appgroup)
                for policyid in appgroup_obj.policies:
                    policy=AppGroupAssociation(
                        policy_id=policyid                    
                    )
                    appgroup.policies.append(policy)
                
                
                session.commit()
                return 0
            except Exception as e:
                session.rollback()
                logging.error(f"an error occurred: {e}")
                raise e
            finally:
                session.close()
        

    @staticmethod
    def read(appgroup_id):
        with GetSession() as session:
            try:
                 return session.query(AppGroup).options(joinedload(AppGroup.policies)).filter_by(id=appgroup_id).first()
            except Exception as e:
                raise e
            finally:
                session.close()
       

    @staticmethod
    def readall():
        with GetSession() as session:
            try:
                 return session.query(AppGroup).\
            options(joinedload(AppGroup.policies).subqueryload(AppGroupAssociation.policy)).\
            order_by(AppGroup.created_on).all()
            except Exception as e:
                raise e
            finally:
                session.close()
        

    @staticmethod
    def update(appgroup_obj,appgroup_id, modified_by):
       with GetSession() as session:
        try:

            appgroup = session.query(AppGroup).filter_by(id=appgroup_id).first()
            if appgroup:
                if AppgroupRepository.validateAppGroup(session,appgroup_obj.name,appgroup_id):
                    return 2
                appgroup.group_name=appgroup_obj.name 
                appgroup.group_desc=appgroup_obj.desc    
                appgroup.modified_by=modified_by
                appgroup.modified_on=getCurrentDateTime()     
                session.query(AppGroupAssociation).filter_by(
                    appgroup_id=appgroup_id).delete()           
                for policyid in appgroup_obj.policies:
                    policy=AppGroupAssociation(
                        policy_id=policyid                    
                    )
                    appgroup.policies.append(policy)
                
                
                session.commit()
                return 0
            return 1
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def delete(appgroup_id):
       with GetSession() as session:
        try:         
            appgroup = session.query(AppGroup).filter_by(id=appgroup_id).first()         
            if appgroup:                
                if(session.query(exists().where(Project.appgroup_id == appgroup_id)).scalar()):
                     return 2
                # all the associations to be deleted before appgroup gets deleted
                # Delete appgroup-policy associations
                session.query(AppGroupAssociation).filter_by(
                    appgroup_id=appgroup_id).delete()
            
                # Delete appgroup
                session.delete(appgroup)
                session.commit()
                return 0
            return 1            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def validateAppGroup(session,group_name,appgroup_id):
       group_name=group_name.strip()
       return session.query(exists().where(and_(AppGroup.id != appgroup_id),(func.lower(AppGroup.group_name)==func.lower(group_name)))).scalar()



    @staticmethod
    def GetAppGroupNameFromProject(session,project_id):
        appgroupname=""
        proj=session.query(Project).filter_by(id=project_id).first()
        if not proj is None:
            apprgroup_id=proj.appgroup_id
            if not apprgroup_id ==None and not apprgroup_id=="":
                appgroup=session.query(AppGroup).filter_by(id=apprgroup_id).first()
                if not appgroup is None:
                    appgroupname=appgroup.group_name
        return appgroupname