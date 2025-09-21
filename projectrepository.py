import logging
import uuid
from repository.dbhandler import GetSession
from util import getCurrentDateTime
from repository.projectpolicyassociation import ProjectPolicyAssociation
from repository.projectentity import Project
from sqlalchemy.orm import joinedload
from repository.policyentity import Policy
from repository.policyllmassociation import PolicyLLMAssociation
from repository.policytopicassociation import PolicyTopicAssociation
from repository.policyregexassociation import PolicyRegexAssociation
from repository.policymetapromptassociation import PolicyMetapromptAssociation
from repository.policyentityassociation import PolicyEntityAssociation
from repository.topicentity import Topic
from repository.llmentity import LLM
from repository.customentity import Entity
from repository.regexentity import Regex
from repository.metapromptentity import Metaprompt
from repository.ProjectPolicyObject import PolicyObject,ProjectPolicyObject,RegexObject,MetPromptObject
from sqlalchemy.sql import and_,exists,func
from repository.policyrepository import PolicyRepository

class ProjectRepository:
    @staticmethod
    def create(proj_obj, modified_by):
        with GetSession() as session:
            try:
                if ProjectRepository.validateProject(session,proj_obj.name,0):
                    return 2
                proj = Project(
                    project_name=proj_obj.name,  
                    appgroup_id=proj_obj.appgroup_id if proj_obj.appgroup_id!="" else None, 
                    project_desc=proj_obj.project_desc,
                    app_ci=proj_obj.app_ci,
                    app_url=proj_obj.app_url,
                    owner_name=proj_obj.owner_name,
                    owner_handle=proj_obj.owner_handle,
                    owner_email=proj_obj.owner_email,
                    approver_name=proj_obj.approver_name,
                    approver_handle=proj_obj.approver_handle,
                    approver_email=proj_obj.approver_email,
                    from_date=proj_obj.from_date,
                    to_date=proj_obj.to_date,
                    locked=proj_obj.locked,
                    active=proj_obj.active,
                    license_key=uuid.uuid4(),              
                    modified_by=modified_by,
                    modified_on=getCurrentDateTime(),
                    created_by=modified_by,
                    created_on=getCurrentDateTime()
                )
                session.add(proj)
                for policyid in proj_obj.policies:
                    policy=ProjectPolicyAssociation(
                        policy_id=policyid                    
                    )
                    proj.policies.append(policy)
                
                
                session.commit()
                return 0
            except Exception as e:
                session.rollback()
                logging.error(f"an error occurred: {e}")
                raise e
            finally:
                session.close()
        

    @staticmethod
    def read(proj_id):
        with GetSession() as session:
            try:
                 return session.query(Project).options(joinedload(Project.policies),joinedload(Project.appgroup)).filter_by(id=proj_id).first()
            except Exception as e:
                raise e
            finally:
                session.close()
       

    @staticmethod
    def readall():
        with GetSession() as session:
            try:
                 return session.query(Project).\
            options(joinedload(Project.policies).subqueryload(ProjectPolicyAssociation.policy),joinedload(Project.appgroup)).\
            order_by(Project.created_on).all()
            except Exception as e:
                raise e
            finally:
                session.close()
        

    @staticmethod
    def update(proj_obj,proj_id, modified_by):
       with GetSession() as session:
        try:

            proj = session.query(Project).filter_by(id=proj_id).first()
            if proj:
                if ProjectRepository.validateProject(session,proj_obj.name,proj_id):
                    return 2
                proj.project_name=proj_obj.name 
                proj.appgroup_id=proj_obj.appgroup_id if proj_obj.appgroup_id!="" else None  
                proj.project_desc=proj_obj.project_desc
                proj.app_ci=proj_obj.app_ci
                proj.app_url=proj_obj.app_url
                proj.owner_name=proj_obj.owner_name
                proj.owner_handle=proj_obj.owner_handle
                proj.owner_email=proj_obj.owner_email
                proj.approver_name=proj_obj.approver_name
                proj.approver_handle=proj_obj.approver_handle
                proj.approver_email=proj_obj.approver_email
                proj.from_date=proj_obj.from_date
                proj.to_date=proj_obj.to_date
                proj.locked=proj_obj.locked
                proj.active=proj_obj.active
                proj.modified_by=modified_by
                proj.modified_on=getCurrentDateTime()     
                session.query(ProjectPolicyAssociation).filter_by(
                    project_id=proj_id).delete()           
                for policyid in proj_obj.policies:
                    policy=ProjectPolicyAssociation(
                        policy_id=policyid                    
                    )
                    proj.policies.append(policy)
                
                
                session.commit()
                return 0
            return 1
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def delete(project_id):
       with GetSession() as session:
        try:
         
            project = session.query(Project).filter_by(id=project_id).first()

            # all the associations to be deleted before project gets deleted
            # Delete project-policy associations
            session.query(ProjectPolicyAssociation).filter_by(
                project_id=project_id).delete()
            
            # Delete project
            session.delete(project)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def validateProject(session,project_name,project_id):
       project_name=project_name.strip()
       return session.query(exists().where(and_(Project.id != project_id),(func.lower(Project.project_name)==func.lower(project_name)))).scalar()
    

    @staticmethod
    def getprojectprompts(project_id):
        with GetSession() as session:
            try:
                proj=session.query(Project).filter_by(id=project_id).first()
                policy_ids=[data.policy_id for data in proj.policies]
                return PolicyRepository.getallpromptsforpolicies(session,policy_ids)
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()

    @staticmethod
    def getprojectpromptsandllms(project_id):
        with GetSession() as session:
            try:
                proj=session.query(Project).filter_by(id=project_id).first()
                policy_ids=[data.policy_id for data in proj.policies]
                prompts= PolicyRepository.getallpromptsforpolicies(session,policy_ids)
                llms= PolicyRepository.getAllLLM(session,policy_ids)
                return [prompts,llms]
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
