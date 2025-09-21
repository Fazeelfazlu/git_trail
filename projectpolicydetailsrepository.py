import logging
import uuid
from repository.dbhandler import GetSession
from repository.admineventlogentity import AdminEventLog
from repository.projectpolicydetailsview import ProjectPolicyDetails
from repository.ProjectPolicyObject import PolicyObject,ProjectPolicyObject,RegexObject,MetPromptObject,LLmObject,PIIObject
from repository.CacheManager import GetProjectFromCache,SetProjectCache
from repository.appgrouprepository import AppgroupRepository
from util import getFormattedDateTimeWithoutTimeZone,getCurrentDateTime
from datareader import readfileAndGetData
from repository.topicrepository import TopicRepository
from repository.versionrepository import VersionRepository
from logger import logger

class ProjectPolicyDetailsRepository:
        @staticmethod
        async def ValidateLicense(proj_id,key,version='guardrail'):
            with GetSession() as session:
                try:     
                    projObj= await GetProjectFromCache(proj_id,key,version)     
                    if projObj is None:  
                        proj=[]
                        topics=[]
                        if version=="pre-prod": 
                            proj=session.query(ProjectPolicyDetails).\
                            filter_by(project_id=proj_id).all()
                            topics=TopicRepository.readalltopics(session)
                            topics=[data.topic_name for data in topics]
                        else:
                            [proj,topics]=VersionRepository.GetProjectForGuardrail(session,str(proj_id),key,version)
                        projObj=ProjectPolicyDetailsRepository.CreateProjEntity(proj,topics)
                        await SetProjectCache(proj_id,key,projObj,version)
                        return projObj
                    else:
                        return projObj
                except Exception as e:
                    raise e
                finally:
                    session.close()
        

        @staticmethod
        def CreateProjEntity(projdetlist,topics=[]):
            if(len(projdetlist)==0):
                return None            
            proj=ProjectPolicyObject(
                id=str(projdetlist[0].project_id),
                project_name=projdetlist[0].project_name,
                project_desc=projdetlist[0].project_desc,
                app_ci=projdetlist[0].app_ci,
                app_url=projdetlist[0].app_url,
                owner_name=projdetlist[0].owner_name,
                owner_handle=projdetlist[0].owner_handle,
                owner_email=projdetlist[0].owner_email,
                approver_name=projdetlist[0].approver_name,
                approver_handle=projdetlist[0].approver_handle,
                approver_email=projdetlist[0].approver_email,
                from_date=projdetlist[0].from_date,
                to_date=projdetlist[0].to_date,
                locked=projdetlist[0].locked,
                active=projdetlist[0].active,               
                policies=[],
                topics=topics                
            )
            
            policy_ids=list(set(data.policy_id for data in projdetlist))
            for policy_id in policy_ids:
                block_pii=list(set((data.block_pii for data in projdetlist if data.policy_id==policy_id)))[0]
                code_checker=list(set((data.code_checker for data in projdetlist if data.policy_id==policy_id)))[0]
                pol=PolicyObject(
                        id=policy_id,
                        policy_name=list(set((data.policy_name for data in projdetlist if data.policy_id==policy_id)))[0],
                        llms=[],
                        block_pii=block_pii,
                        code_checker=code_checker,
                        anonymize= list(set((data.anonymize for data in projdetlist if data.policy_id==policy_id)))[0],
                        injectionthreshold=list(set((data.injectionthreshold for data in projdetlist if data.policy_id==policy_id)))[0],
                        hatefulsentimentthreshold=list(set((data.hatefulsentimentthreshold for data in projdetlist if data.policy_id==policy_id)))[0],
                        toxicitythreshold=list(set((data.toxicitythreshold for data in projdetlist if data.policy_id==policy_id)))[0], 
                        topics=list(set((data.topic_name for data in projdetlist if data.policy_id==policy_id))),
                        regexs=[],
                        entities=list(set((data.entity_value for data in projdetlist if data.policy_id==policy_id))),
                        metaprompts=[],
                        policy_type=list(set((data.policy_type for data in projdetlist if data.policy_id==policy_id)))[0],
                        log_level=list(set((data.log_level for data in projdetlist if data.policy_id==policy_id)))[0],
                        pii_names=[],
                        banned_phrases=list(set((data.banned_phrase for data in projdetlist if data.policy_id==policy_id))),
                )
                regexList=list(set(((data.regex_name,data.regex_value) for data in projdetlist if data.policy_id==policy_id)))
                for regex_name,regex_value in regexList:
                    regexObj=RegexObject(
                        regex_name=regex_name,
                        regex_value=regex_value
                    )
                    pol.regexs.append(regexObj)
                metapromptList=list(set(((data.metaprompt_id,data.metaprompt_value,data.metaprompt_name) for data in projdetlist if data.policy_id==policy_id)))
                for metapromptid,metaprompt_value,metaprompt_name in metapromptList:
                    metaprompt=MetPromptObject(
                        metapromptid=metapromptid,
                        metaprompt_value=metaprompt_value,
                        metaprompt_name=metaprompt_name
                    )
                    pol.metaprompts.append(metaprompt)   
                llmList=list(set(((data.llm_name,data.watermark_text) for data in projdetlist if data.policy_id==policy_id)))
                for llm_name,watermark_text in llmList:
                   llmObj=LLmObject(
                        llm=llm_name,
                        watermark_text=watermark_text
                    )
                   pol.llms.append(llmObj)
                piilist=list(set(((data.pii_name,data.pii_desc) for data in projdetlist if data.policy_id==policy_id)))
                for pii_name,pii_desc in piilist:
                   piiobj=PIIObject(
                        pii_name=pii_name,
                        pii_desc=pii_desc
                    )
                   pol.pii_names.append(piiobj)
                proj.policies.append(pol)
            return proj
        



        @staticmethod
        def GetProjectView(proj_id,constants):
            with GetSession() as session:
                try:    
                    proj=session.query(ProjectPolicyDetails).\
                    filter_by(project_id=proj_id).all()
                    projObj=ProjectPolicyDetailsRepository.CreateProjEntity(proj)  
                    proj_det=ProjectPolicyDetailsRepository.CreateProjectSingleView(projObj,constants)  
                    proj_det["appgroup_id"]= AppgroupRepository.GetAppGroupNameFromProject(session,proj_id)                  
                    return proj_det
                   
                except Exception as e:
                    raise e
                finally:
                    session.close()


        @staticmethod
        def CreateProjectSingleView(ProjectObject,constants):
            proj_det={
                'id':ProjectObject.id,
                'name':ProjectObject.project_name,
                'project_desc':ProjectObject.project_desc,
                'app_ci':ProjectObject.app_ci,
                'app_url':ProjectObject.app_url,
                'owner_name':ProjectObject.owner_name,
                'owner_handle':ProjectObject.owner_handle,
                'owner_email':ProjectObject.owner_email,
                'approver_name':ProjectObject.approver_name,
                'approver_handle':ProjectObject.approver_handle,
                'approver_email':ProjectObject.approver_email,
                'from_date':getFormattedDateTimeWithoutTimeZone(ProjectObject.from_date) if not ProjectObject.from_date==None else "",
                'to_date':getFormattedDateTimeWithoutTimeZone(ProjectObject.to_date) if not ProjectObject.to_date==None else "",
                'locked':ProjectObject.locked,
                'active':ProjectObject.active,
                 'block_pii':'',
                 'code_checker':'',
                 'anonymize':'',
                'injectionthreshold': 1.0,
                'hatefulsentimentthreshold': -1.0,
                'toxicitythreshold': 1.0,
                 'piientities':{
                     'blocked':[],
                     'logged':[]
                 },
                'topics':{
                     'blocked':[],
                     'logged':[]
                 },
                 'regex':{
                     'blocked':[],
                     'logged':[]
                 },
                   'entities':{
                     'blocked':[],
                     'logged':[]
                 },
                    'llms':[],
                    'metaprompts':[],
                    'phrases':{
                     'blocked':[],
                     'logged':[]
                 },
                 'policies':[policy.policy_name for policy in ProjectObject.policies]

            }
            blocked_policies=[policy for policy in ProjectObject.policies if policy.policy_type==constants["POLICY_TYPE"]["BLOCK"]]
            logged_policies=[policy for policy in ProjectObject.policies if policy.policy_type==constants["POLICY_TYPE"]["LOG"]]
           
            pii_blocked_policy=[]
            pii_logged_policy=[]
            code_blocked_policy=[]
            code_logged_policy=[]
            anonymize_policy=[]
            metaprompts=[]
            llms=[]
            blocked_pii=[]
            logged_pii=[]
            blocked_topic=[]
            logged_topic=[]
            blocked_phrases=[]
            logged_phrases=[]
            blocked_regex=[]
            logged_regex=[]
            blocked_entities=[]
            logged_entities=[]
            for policy in blocked_policies:
                if policy.block_pii=="Y":
                    pii_blocked_policy.append(policy.policy_name)
                if policy.code_checker=="Y":
                    code_blocked_policy.append(policy.policy_name)
                if policy.anonymize=="Y":
                    anonymize_policy.append(policy.policy_name)
                if proj_det["injectionthreshold"]>policy.injectionthreshold:
                    proj_det["injectionthreshold"]=policy.injectionthreshold
                if proj_det["hatefulsentimentthreshold"]<policy.hatefulsentimentthreshold:
                    proj_det["hatefulsentimentthreshold"]=policy.hatefulsentimentthreshold
                if proj_det["toxicitythreshold"]>policy.toxicitythreshold:
                    proj_det["toxicitythreshold"]=policy.toxicitythreshold
                if len(policy.metaprompts)>0:
                    for metaprompt in policy.metaprompts:
                        if metaprompt and metaprompt.metaprompt_name:
                            if not metaprompt.metapromptid  in [data['metapromptid'] for data in metaprompts]:
                                metaprompts.append({
                                    "metapromptid":metaprompt.metapromptid,
                                'metaprompt_name':metaprompt.metaprompt_name,  
                                    'policies':[policy.policy_name]
                                })
                            else:
                                metaprompt=[data for data in metaprompts if data['metapromptid']==metaprompt.metapromptid][0]
                                metaprompt["policies"].append(policy.policy_name)
                if len(policy.llms)>0:
                    for llmobj in policy.llms:  
                        if llmobj and   llmobj.llm:                   
                            if not llmobj.llm  in [data['llm'] for data in llms]:
                                llms.append({
                                    "llm":llmobj.llm,
                                    'policies':[policy.policy_name]
                                })
                            else:
                                llm=[data for data in llms if data['llm']==llmobj.llm][0]
                                llm["policies"].append(policy.policy_name)
                if len(policy.pii_names)>0:
                    for piiobj in policy.pii_names:
                        if piiobj and piiobj.pii_desc:
                            if not piiobj.pii_desc  in [data['pii_name'] for data in blocked_pii]:
                                blocked_pii.append({
                                    "pii_name":piiobj.pii_desc,                                
                                    'policies':[policy.policy_name]
                                })
                            else:
                                pii=[data for data in blocked_pii if data['pii_name']==piiobj.pii_desc][0]
                                pii["policies"].append(policy.policy_name)
                if len(policy.topics)>0:
                    for topic in policy.topics:
                        if topic:
                            if not topic  in [data['topic'] for data in blocked_topic]:
                                blocked_topic.append({
                                    "topic":topic,                                
                                    'policies':[policy.policy_name]
                                })
                            else:
                                topicdet=[data for data in blocked_topic if data['topic']==topic][0]
                                topicdet["policies"].append(policy.policy_name)
                if len(policy.banned_phrases)>0:
                    for phrases in policy.banned_phrases:
                        if phrases:
                            if not phrases  in [data['phrases'] for data in blocked_phrases]:
                                blocked_phrases.append({
                                    "phrases":phrases,                                
                                    'policies':[policy.policy_name]
                                })
                            else:
                                phrasesdet=[data for data in blocked_phrases if data['phrases']==phrases][0]
                                phrasesdet["policies"].append(policy.policy_name)

                if len(policy.regexs)>0:
                    for regex in policy.regexs:
                        if regex and regex.regex_name:
                            if not regex.regex_name  in [data['regex_name'] for data in blocked_regex]:
                                blocked_regex.append({
                                    "regex_name":regex.regex_name,                                
                                    'policies':[policy.policy_name]
                                })
                            else:
                                pii=[data for data in blocked_regex if data['regex_name']==regex.regex_name][0]
                                pii["policies"].append(policy.policy_name)      

                if len(policy.entities)>0:
                    for entity in policy.entities:
                        if entity:
                            if not entity  in [data['entity'] for data in blocked_entities]:
                                blocked_entities.append({
                                    "entity":entity,                                
                                    'policies':[policy.policy_name]
                                })
                            else:
                                entitydet=[data for data in blocked_entities if data['entity']==entity][0]
                                entitydet["policies"].append(policy.policy_name)



            for policy in logged_policies:
                if policy.block_pii=="Y":
                    pii_logged_policy.append(policy.policy_name)
                if policy.code_checker=="Y":
                    code_logged_policy.append(policy.policy_name)
                if policy.anonymize=="Y":
                    anonymize_policy.append(policy.policy_name)
                if len(policy.metaprompts)>0:
                    for metaprompt in policy.metaprompts:
                         if metaprompt and metaprompt.metaprompt_name:
                            if not metaprompt.metapromptid  in [data['metapromptid'] for data in metaprompts]:
                                metaprompts.append({
                                    "metapromptid":metaprompt.metapromptid,
                                    'metaprompt_name':metaprompt.metaprompt_name,                                
                                    'policies':[policy.policy_name]
                                })
                            else:
                                metaprompt=[data for data in metaprompts if data['metapromptid']==metaprompt.metapromptid][0]
                                metaprompt["policies"].append(policy.policy_name)
                if len(policy.llms)>0:
                    for llmobj in policy.llms:
                         if llmobj and   llmobj.llm:          
                            if not llmobj.llm  in [data['llm'] for data in llms]:
                                llms.append({
                                    "llm":llmobj.llm,
                                    'policies':[policy.policy_name]
                                })
                            else:
                                llm=[data for data in llms if data['llm']==llmobj.llm][0]
                                llm["policies"].append(policy.policy_name)

                if len(policy.pii_names)>0:
                    for piiobj in policy.pii_names:
                        if piiobj and piiobj.pii_desc:
                            if not piiobj.pii_desc  in [data['pii_name'] for data in logged_pii]:
                                logged_pii.append({
                                    "pii_name":piiobj.pii_desc,                                
                                    'policies':[policy.policy_name]
                                })
                            else:
                                pii=[data for data in logged_pii if data['pii_name']==piiobj.pii_desc][0]
                                pii["policies"].append(policy.policy_name)
                if len(policy.topics)>0:
                    for topic in policy.topics:
                        if topic:
                            if not topic  in [data['topic'] for data in logged_topic]:
                                logged_topic.append({
                                    "topic":topic,                                
                                    'policies':[policy.policy_name]
                                })
                            else:
                                topicdet=[data for data in logged_topic if data['topic']==topic][0]
                                topicdet["policies"].append(policy.policy_name)
                if len(policy.banned_phrases)>0:
                    for phrases in policy.banned_phrases:
                        if phrases:
                            if not phrases  in [data['phrases'] for data in logged_phrases]:
                                logged_phrases.append({
                                    "phrases":phrases,                                
                                    'policies':[policy.policy_name]
                                })
                            else:
                                phrasesdet=[data for data in logged_phrases if data['phrases']==phrases][0]
                                phrasesdet["policies"].append(policy.policy_name)

                if len(policy.regexs)>0:
                    for regex in policy.regexs:
                        if regex and regex.regex_name:
                            if not regex.regex_name  in [data['regex_name'] for data in logged_regex]:
                                logged_regex.append({
                                    "regex_name":regex.regex_name,                                
                                    'policies':[policy.policy_name]
                                })
                            else:
                                pii=[data for data in logged_regex if data['regex_name']==regex.regex_name][0]
                                pii["policies"].append(policy.policy_name)  

                if len(policy.entities)>0:
                    for entity in policy.entities:
                        if entity:
                            if not entity  in [data['entity'] for data in logged_entities]:
                                logged_entities.append({
                                    "entity":entity,                                
                                    'policies':[policy.policy_name]
                                })
                            else:
                                entitydet=[data for data in logged_entities if data['entity']==entity][0]
                                entitydet["policies"].append(policy.policy_name) 

                if proj_det["injectionthreshold"]>policy.injectionthreshold:
                    proj_det["injectionthreshold"]=policy.injectionthreshold
                if proj_det["hatefulsentimentthreshold"]<policy.hatefulsentimentthreshold:
                    proj_det["hatefulsentimentthreshold"]=policy.hatefulsentimentthreshold
                if proj_det["toxicitythreshold"]>policy.toxicitythreshold:
                    proj_det["toxicitythreshold"]=policy.toxicitythreshold


            if len(pii_blocked_policy) >0:
                proj_det['block_pii']=f"Blocked ({','.join(pii_blocked_policy)})"
            elif len(pii_logged_policy) >0:
                proj_det['block_pii']=f"Logged ({','.join(pii_logged_policy)})"
            else:
                proj_det['block_pii']="None"

            if len(code_blocked_policy) >0:
                proj_det['code_checker']=f"Blocked ({','.join(code_blocked_policy)})"
            elif len(code_logged_policy) >0:
                proj_det['code_checker']=f"Logged ({','.join(code_logged_policy)})"
            else:
                proj_det['code_checker']="None"
            

            if len(anonymize_policy) >0:
                proj_det['anonymize']=f"Yes ({','.join(anonymize_policy)})"
            else:
                proj_det['anonymize']="No"


            if len(metaprompts)>0:
                for metaprompt in metaprompts:
                    proj_det['metaprompts'].append(f"{metaprompt['metaprompt_name']} ({','.join(metaprompt['policies'])})")

            if len(llms)>0:
                for llm in llms:
                    proj_det['llms'].append(f"{llm['llm']} ({','.join(llm['policies'])})")
            
            if len(blocked_pii)>0:
                for pii in blocked_pii:
                    proj_det ['piientities']['blocked'].append(f"{pii['pii_name']} ({','.join(pii['policies'])})")
           
            if len(logged_pii)>0:
                for pii in logged_pii:
                    proj_det ['piientities']['logged'].append(f"{pii['pii_name']} ({','.join(pii['policies'])})")

            if len(blocked_topic)>0:
                for topic in blocked_topic:
                    proj_det ['topics']['blocked'].append(f"{topic['topic']} ({','.join(topic['policies'])})")
           
            if len(logged_topic)>0:
                for topic in logged_topic:
                    proj_det ['topics']['logged'].append(f"{topic['topic']} ({','.join(topic['policies'])})")

            if len(blocked_phrases)>0:
                for phrases in blocked_phrases:
                    proj_det ['phrases']['blocked'].append(f"{phrases['phrases']} ({','.join(phrases['policies'])})")
           
            if len(logged_phrases)>0:
                for phrases in logged_phrases:
                    proj_det ['phrases']['logged'].append(f"{phrases['phrases']} ({','.join(phrases['policies'])})")

            if len(blocked_regex)>0:
                for regex in blocked_regex:
                    proj_det ['regex']['blocked'].append(f"{regex['regex_name']} ({','.join(regex['policies'])})")
           
            if len(logged_regex)>0:
                for regex in logged_regex:
                    proj_det ['regex']['logged'].append(f"{regex['regex_name']} ({','.join(regex['policies'])})")


            if len(blocked_entities)>0:
                for entity in blocked_entities:
                    proj_det ['entities']['blocked'].append(f"{entity['entity']} ({','.join(entity['policies'])})")
           
            if len(logged_entities)>0:
                for entity in logged_entities:
                    proj_det ['entities']['logged'].append(f"{entity['entity']} ({','.join(entity['policies'])})")

            return proj_det


        @staticmethod
        def PublishProject(proj_id,published_by):
              with GetSession() as session:
                try:     
                    proj=session.query(ProjectPolicyDetails).\
                    filter_by(project_id=proj_id).all()
                    topics=TopicRepository.readalltopics(session)
                    if proj[0].active=="Y" and proj[0].locked=="N":
                        (result,version)=VersionRepository.createNewVersion(session,str(proj_id),proj,topics,published_by,False) 
                        
                        constants= readfileAndGetData("constants")
                        log = AdminEventLog(eventname = constants["ADMIN_EVENTS"]["APP_PUBLISH"],
                                            project_id = proj_id,
                                            new_value = version,
                                            created_by = published_by,
                                            created_on = getCurrentDateTime(),
                                            prev_value = ""
                                            )
                        session.add(log)
                        session.commit()
                        return result
                    else:
                        return 1
                except Exception as e:
                    session.rollback()
                    logging.error(f"an error occurred: {e}")
                    raise e
                finally:
                    session.close()


        @staticmethod
        def GetPublishedProjectDetails(project_id,constants,versionid):
             with GetSession() as session:
                try:
                    if versionid == 'latest':
                        proj=VersionRepository.GetProjectDetails(session,project_id)                        
                    else :
                        proj = VersionRepository.GetProjectDetailsFrmVersion(session,project_id,versionid)
                    projObj=ProjectPolicyDetailsRepository.CreateProjEntity(proj)  
                    proj_det=ProjectPolicyDetailsRepository.CreateProjectSingleView(projObj,constants)    
                    return proj_det  
                except Exception as e:
                    raise e
                finally:
                    session.close()