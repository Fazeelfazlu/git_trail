import logging
import uuid
from repository.dbhandler import GetSession
from util import getCurrentDateTime
from repository.versionappentity import VersionedApp
from repository.publishedappentity import PublishedApp
from repository.appversionentity import AppVersion
from repository.publishedtopicentity import PublishedTopic
from repository.versionedtopicentity import VersionedTopic
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import and_,exists,func
from datareader import readfileAndGetData
from repository.admineventlogentity import AdminEventLog

class VersionRepository:

    @staticmethod
    def getLastVersionNumber(session,project_id):
        versions=session.query(AppVersion.version_no).filter_by(project_id=project_id).all()
        versionNums=[]
        if versions and  len(versions) >0:
            for version in versions:
                versionNums.append(int(version[0].replace("R:","")))
        if len(versionNums)>0:
            return max(versionNums)
        else:
            return 0

    @staticmethod
    def getLatestVersion(session,project_id):
        return session.query(AppVersion).filter_by(project_id=project_id,is_latest="Y").first()
       

    @staticmethod
    def createNewVersion(session,project_id,appdata,topics,created_by,rollbackflag=False,rollbackversion=0):
       currentversion=session.query(PublishedApp).filter_by(project_id=project_id).first()
       if currentversion and (currentversion.active=="N" or currentversion.locked=="Y"):
           return (2,None)
       lastVersionNumber= VersionRepository.getLastVersionNumber(session,project_id)      
       newVersionNumber=0
       if not rollbackflag:
        newVersionNumber=lastVersionNumber+1
       else:
        newVersionNumber=f"R:{rollbackversion}"
       latestVersion=VersionRepository.getLatestVersion(session,project_id)
       if latestVersion:
            latestVersion.is_latest="N"
            lastappdata=session.query(PublishedApp).filter_by(project_id=project_id).all()
            for lastdata in lastappdata:
                versionedapp= VersionedApp( project_id = project_id,
                                policy_id =lastdata.policy_id,
                                llm_name = lastdata.llm_name,
                                log_level=lastdata.log_level,
                                code_checker=lastdata.code_checker,
                                anonymize=lastdata.anonymize,
                                block_pii=lastdata.block_pii,
                                policy_type=lastdata.policy_type,
                                topic_name=lastdata.topic_name,
                                regex_name = lastdata.regex_name,
                                regex_value = lastdata.regex_value,
                                metaprompt_id = lastdata.metaprompt_id,
                                metaprompt_value = lastdata.metaprompt_value,
                                entity_value =lastdata.entity_value,
                                license_key=lastdata.license_key,
                                watermark_text=lastdata.watermark_text,
                                pii_name =lastdata.pii_name,
                                pii_desc = lastdata.pii_desc,
                                banned_phrase=lastdata.banned_phrase,
                                project_name = lastdata.project_name,
                                policy_name = lastdata.policy_name, 
                                metaprompt_name =lastdata.metaprompt_name,
                                injectionthreshold=lastdata.injectionthreshold,
                                hatefulsentimentthreshold=lastdata.hatefulsentimentthreshold,
                                toxicitythreshold=lastdata.toxicitythreshold,
                                project_desc  =lastdata.project_desc,
                                app_ci=lastdata.app_ci,
                                app_url=lastdata.app_url, 
                                owner_name=lastdata.owner_name,
                                owner_handle=lastdata.owner_handle,
                                owner_email=lastdata.owner_email,
                                approver_name=lastdata.approver_name,
                                approver_handle=lastdata.approver_handle,
                                approver_email=lastdata.approver_email,
                                from_date=lastdata.from_date,
                                to_date=lastdata.to_date,
                                locked=lastdata.locked,
                                active=lastdata.active,
                                created_on = lastdata.created_on
                            )
                latestVersion.versionedapp.append(versionedapp)
            lasttopics=session.query(PublishedTopic).filter_by(project_id=project_id).all()
            for topic in lasttopics:
                versionedtopic=VersionedTopic(
                    project_id=project_id,
                    topic_name=topic.topic_name,
                      created_on = topic.created_on
                )
                latestVersion.topics.append(versionedtopic)

       newversion=  AppVersion(
           project_id=project_id,
           version_no=str(newVersionNumber),
           is_latest="Y",
           created_on=getCurrentDateTime(),
           created_by=created_by
       )
       session.add(newversion)
       session.query(PublishedApp).filter_by(
                project_id=project_id).delete()
       session.query(PublishedTopic).filter_by(
                project_id=project_id).delete()
       currentTime= getCurrentDateTime()
       for data in appdata:
           app= PublishedApp( project_id = project_id,
                                policy_id =data.policy_id,
                                llm_name = data.llm_name,
                                log_level=data.log_level,
                                code_checker=data.code_checker,
                                anonymize=data.anonymize,
                                block_pii=data.block_pii,
                                policy_type=data.policy_type,
                                topic_name=data.topic_name,
                                regex_name = data.regex_name,
                                regex_value = data.regex_value,
                                metaprompt_id = data.metaprompt_id,
                                metaprompt_value = data.metaprompt_value,
                                entity_value =data.entity_value,
                                license_key=data.license_key,
                                watermark_text=data.watermark_text,
                                pii_name =data.pii_name,
                                pii_desc = data.pii_desc,
                                banned_phrase=data.banned_phrase,
                                project_name = data.project_name,
                                policy_name = data.policy_name, 
                                metaprompt_name =data.metaprompt_name,
                                injectionthreshold=data.injectionthreshold,
                                hatefulsentimentthreshold=data.hatefulsentimentthreshold,
                                toxicitythreshold=data.toxicitythreshold,
                                project_desc  =data.project_desc,
                                app_ci=data.app_ci,
                                app_url=data.app_url, 
                                owner_name=data.owner_name,
                                owner_handle=data.owner_handle,
                                owner_email=data.owner_email,
                                approver_name=data.approver_name,
                                approver_handle=data.approver_handle,
                                approver_email=data.approver_email,
                                from_date=data.from_date,
                                to_date=data.to_date,
                                locked=data.locked,
                                active=data.active,
                                created_on = currentTime,
                                modified_on=currentTime,
                                created_by=created_by,
                                modified_by=created_by
                            )
           session.add(app)

       for topic in topics:
           publisedtopic=PublishedTopic(
                    project_id=project_id,
                    topic_name=topic.topic_name,
                    created_on = currentTime
                )
           session.add(publisedtopic)
       return (0,str(newVersionNumber))


    @staticmethod
    def getinactiveVersions(project_id):
        with GetSession() as session:
            try:       
               return session.query(AppVersion).filter_by(project_id=project_id,is_latest="N").\
                     order_by(AppVersion.created_on.desc()).all()
                
            except Exception as e:            
                raise e
            finally:
                session.close()


       
    @staticmethod
    def rollbackversion(project_id,version_id,rolledback_by):
        with GetSession() as session:
            try:       
                version= session.query(AppVersion).filter_by(project_id=project_id,id=version_id).first()                  
                version_num=version.version_no
                lastversionAppData=session.query(VersionedApp).filter_by(project_id=project_id,version_id=version_id).all()
                lastversionTopics=session.query(VersionedTopic).filter_by(project_id=project_id,version_id=version_id).all()
                (result,version) = VersionRepository.createNewVersion(session,project_id,lastversionAppData,lastversionTopics,rolledback_by,True,version_num)
                
                constants= readfileAndGetData("constants")
                log = AdminEventLog(eventname = constants["ADMIN_EVENTS"]["ROLLBACK_APPLICATION"],
                                    project_id = project_id,
                                    new_value = version,
                                    created_by = rolledback_by,
                                    created_on = getCurrentDateTime(),
                                    prev_value = version_num
                                    )
                session.add(log)
                
                session.commit()
                return result
            except Exception as e: 
                session.rollback()
                raise e
            finally:
                session.close()



    @staticmethod
    def getallpublishedProjects():
         with GetSession() as session:
            try:      
              
              projects= session.query(PublishedApp.project_id,PublishedApp.project_name,PublishedApp.project_desc,PublishedApp.created_on,PublishedApp.active,PublishedApp.locked,PublishedApp.created_by,PublishedApp.modified_by,PublishedApp.modified_on).order_by(PublishedApp.created_on).distinct()            
              activeVersions=VersionRepository.GetAllActiveVersions(session=session)            
              return [projects,activeVersions]
            except Exception as e:
              
                raise e
            finally:
                session.close()


    @staticmethod
    def GetProjectDetails(session,project_id):      
            return session.query(PublishedApp).filter_by(project_id=project_id).all()
    
    @staticmethod
    def GetProjectDetailsFrmVersion(session,project_id,versionid):      
            return session.query(VersionedApp).filter_by(project_id=project_id,version_id=versionid).all()
    


    @staticmethod
    def activedeactive(project_id,activateflag,modifiedBy):
         with GetSession() as session:
            try:       
              currentTime=getCurrentDateTime()
              session.query(PublishedApp).filter_by(project_id=project_id).update({
                  PublishedApp.active:activateflag,
                  PublishedApp.modified_by:modifiedBy,
                  PublishedApp.modified_on:currentTime
              }                  
              ) 
              
              constants= readfileAndGetData("constants")
              log = AdminEventLog(eventname = (constants["ADMIN_EVENTS"]["DEACTIVE_APPLICATION"]) if activateflag=="N" else (constants["ADMIN_EVENTS"]["ACTIVE_APPLICATION"]),
                                project_id = project_id,
                                new_value = "Active" if activateflag=="Y" else "Deactive",
                                created_by = modifiedBy,
                                created_on = getCurrentDateTime(),
                                prev_value = "Active" if activateflag=="N" else "Deactive"
                                )
              session.add(log)          
              session.commit()
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
    

    @staticmethod
    def lockedunlock(project_id,lockedFlag,modifiedBy):
         with GetSession() as session:
            try:       
              currentTime=getCurrentDateTime()
              session.query(PublishedApp).filter_by(project_id=project_id).update({
                  PublishedApp.locked:lockedFlag,
                  PublishedApp.modified_by:modifiedBy,
                  PublishedApp.modified_on:currentTime
              }) 
              
              constants= readfileAndGetData("constants")
              log = AdminEventLog(eventname = (constants["ADMIN_EVENTS"]["LOCK_APPLICATION"]) if lockedFlag=="Y" else (constants["ADMIN_EVENTS"]["UNLOCK_APPLICATION"]),
                                project_id = project_id,
                                new_value = "Locked" if lockedFlag=="Y" else "Unlocked",
                                created_by = modifiedBy,
                                created_on = getCurrentDateTime(),
                                prev_value = "Unlocked" if lockedFlag=="Y" else "Locked"
                                )
              session.add(log)     
              
              session.commit()
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()


    @staticmethod
    def getProjectForConfig(project_id):
         with GetSession() as session:
            try:       
              project= session.query(PublishedApp.project_id,PublishedApp.license_key).filter_by(project_id=project_id).first()                 
              return project
            except Exception as e:
              
                raise e
            finally:
                session.close()


    @staticmethod
    def exportprojectdata(project_id):
         with GetSession() as session:
            try:       
              project= session.query(PublishedApp).filter_by(project_id=project_id).all()   
              topics=session.query(PublishedTopic).filter_by(project_id=project_id).all()      
              return [project,topics]
            except Exception as e:              
                raise e
            finally:
                session.close()


    @staticmethod
    def ImportProject(project_id,projdata,topicdata,imported_by):
        projects=[]
        topics=[]
        for proj in projdata:
            objproj=VersionedApp( project_id = proj['project_id'],
                                policy_id =proj['policy_id'],
                                llm_name = proj['llm_name'],
                                log_level=proj['log_level'],
                                code_checker=proj['code_checker'],
                                anonymize=proj['anonymize'],
                                block_pii=proj['block_pii'],
                                policy_type=proj['policy_type'],
                                topic_name=proj['topic_name'],
                                regex_name = proj['regex_name'],
                                regex_value = proj['regex_value'],
                                metaprompt_id = proj['metaprompt_id'],
                                metaprompt_value = proj['metaprompt_value'],
                                entity_value =proj['entity_value'],
                                license_key=proj['license_key'],
                                watermark_text=proj['watermark_text'],
                                pii_name =proj['pii_name'],
                                pii_desc = proj['pii_desc'],
                                banned_phrase=proj['banned_phrase'],
                                project_name = proj['project_name'],
                                policy_name = proj['policy_name'], 
                                metaprompt_name =proj['metaprompt_name'],
                                injectionthreshold=proj['injectionthreshold'],
                                hatefulsentimentthreshold=proj['hatefulsentimentthreshold'],
                                toxicitythreshold=proj['toxicitythreshold'],
                                project_desc  =proj['project_desc'],
                                app_ci=proj['app_ci'],
                                app_url=proj['app_url'], 
                                owner_name=proj['owner_name'],
                                owner_handle=proj['owner_handle'],
                                owner_email=proj['owner_email'],
                                approver_name=proj['approver_name'],
                                approver_handle=proj['approver_handle'],
                                approver_email=proj['approver_email'],
                                from_date=proj['from_date'],
                                to_date=proj['to_date'],
                                locked=proj['locked'],
                                active=proj['active'],
                                created_on = proj['created_on']
                            )
            projects.append(objproj)
        for topic in topicdata:
            objTopic=VersionedTopic(
                project_id=topic['project_id'],
                topic_name=topic['topic_name'],
                    created_on = topic['created_on']
            )
            topics.append(objTopic)
        with GetSession() as session:
            try:      
                (result,version) =VersionRepository.createNewVersion(session,project_id,projects,topics,imported_by,rollbackflag=False,rollbackversion=0)  
                
                constants= readfileAndGetData("constants")
                log = AdminEventLog(eventname = constants["ADMIN_EVENTS"]["IMPORT_APPLICATION"],
                                    project_id = project_id,
                                    new_value = version,
                                    created_by = imported_by,
                                    created_on = getCurrentDateTime(),
                                    prev_value = ""
                                    )
                session.add(log)
                        
                session.commit()    
                return result
            except Exception as e:     
                session.rollback()         
                raise e
            finally:
                session.close()

    @staticmethod
    def getAllVersions(project_id):
        with GetSession() as session:
            try:       
               return session.query(AppVersion).filter_by(project_id=project_id).\
                     order_by(AppVersion.created_on.desc()).all()
                
            except Exception as e:            
                raise e
            finally:
                session.close()

    @staticmethod
    def GetProjectPolicyForDashboard():
         with GetSession() as session:
            try:       
               data= session.query(PublishedApp.project_id,PublishedApp.project_name,PublishedApp.policy_id,PublishedApp.policy_name).distinct()
               projects=[]
               policies=[]
               for record in data:
                   if len([data for data in policies if data["id"]==record[2]])==0:
                       objpolicy={
                           "id":record[2],
                           "name":record[3]
                         }
                       policies.append(objpolicy)
                   if len([data for data in projects if data["id"]==record[0]])==0:
                       objproject={
                           "id":record[0],
                           "name":record[1],
                           "policies":[record[2]]
                         }
                       projects.append(objproject)
                   else:
                       objproject=[data for data in projects if data["id"]==record[0]][0]
                       if len([data for data in objproject["policies"] if data==record[2]])==0:
                           objproject["policies"].append(record[2])
               return [projects,policies]
            except Exception as e:            
                raise e
            finally:
                session.close()


    
    @staticmethod
    def GetProjectForGuardrail(session,project_id,key,version_id):
        proj=[]
        topics=[]
        if version_id=='guardrail':
            proj= session.query(PublishedApp).filter_by(project_id=project_id,license_key=key).all()
            topics=session.query(PublishedTopic).filter_by(project_id=project_id).all()
        elif version_id=='latest':
            proj= session.query(PublishedApp).filter_by(project_id=project_id).all()
            topics=session.query(PublishedTopic).filter_by(project_id=project_id).all()
        else:
            proj= session.query(VersionedApp).filter_by(project_id=project_id,version_id=version_id).all()
            topics= session.query(VersionedTopic).filter_by(project_id=project_id,version_id=version_id).all()
        topics=[data.topic_name for data in topics]
        return [proj,topics]

            
    @staticmethod
    def GetAllActiveVersions(session):
        return session.query(AppVersion).filter_by(is_latest="Y").all()
    


    @staticmethod
    def deletepublishedapp(project_id):
           with GetSession() as session:
            try:      
                session.query(PublishedApp).filter_by(project_id=project_id).delete()
                session.query(PublishedTopic).filter_by(project_id=project_id).delete()
                session.query(VersionedApp).filter_by(project_id=project_id).delete()
                session.query(VersionedTopic).filter_by(project_id=project_id).delete()
                session.query(AppVersion).filter_by(project_id=project_id).delete()                
                session.commit()    
                return True
            except Exception as e:     
                session.rollback()         
                raise e
            finally:
                session.close()