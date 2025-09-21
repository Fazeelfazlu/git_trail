import logging
from repository.policyentity import Policy
from repository.dbhandler import GetSession
from util import getCurrentDateTime
from repository.policytopicassociation import PolicyTopicAssociation
from repository.policyregexassociation import PolicyRegexAssociation
from repository.policymetapromptassociation import PolicyMetapromptAssociation
from repository.policyentityassociation import PolicyEntityAssociation
from repository.policyllmassociation import PolicyLLMAssociation
from repository.projectpolicyassociation import ProjectPolicyAssociation
from repository.appgrouppolicyassoc import AppGroupAssociation
from repository.piientitypolicyassoc import PIIPolicyAssociation
from repository.bannedphraseentity import BannedPhrases
from repository.policygeographyentity import PolicyGeography
from datareader import readfileAndGetData
from sqlalchemy.orm import joinedload
from repository.CacheManager import SetPolicyDetCache,GetPolicyDetFromCache
from sqlalchemy.sql import exists,and_,func
from repository.promptrepository import PromptRepository
from logger import logger

class PolicyRepository:
    @staticmethod
    def create(policy_obj, modified_by):
        with GetSession() as session:
            try:     
                if PolicyRepository.validatePolicy(session,policy_obj.name,0) :
                    return [2,None]
                constants=readfileAndGetData("constants")
                policy = Policy(
                    policy_name=policy_obj.name,
                    policy_desc= policy_obj.policy_desc,
                    industry=policy_obj.industry, 
                    log_level=policy_obj.log_level,
                    code_checker=policy_obj.code_checker,
                    anonymize=policy_obj.anonymize,
                    block_pii="Y" if len(policy_obj.piientities)>0 else "N",             
                    policy_type=policy_obj.policy_type ,        
                    injectionthreshold=policy_obj.injectionthreshold,
                    hatefulsentimentthreshold=policy_obj.hatefulsentimentthreshold,
                    toxicitythreshold=policy_obj.toxicitythreshold,                   
                    modified_by=modified_by,
                    modified_on=getCurrentDateTime(),
                    created_by=modified_by,
                    created_on=getCurrentDateTime()
                )
                session.add(policy)
                for blocked_topic in policy_obj.topics:
                    policy_topic=PolicyTopicAssociation(
                        topic_id=blocked_topic                    
                    )
                    policy.topics.append(policy_topic)
                
                for blocked_regex in policy_obj.regexs:
                    policy_regex=PolicyRegexAssociation(
                        regex_id=blocked_regex
                    
                    )
                    policy.regexs.append(policy_regex)
                
                for blocked_metaprompt in policy_obj.metaprompts:
                    policy_metaprompt = PolicyMetapromptAssociation(
                        metaprompt_id=blocked_metaprompt
                    
                    )
                    policy.metaprompts.append(policy_metaprompt)
                for blocked_entity in policy_obj.entities:
                    policy_entity=PolicyEntityAssociation(
                        entity_id=blocked_entity                  
                    )
                    policy.entities.append(policy_entity)
                for llm in policy_obj.llms:
                    policy_llm=PolicyLLMAssociation(
                        llm_id=llm                 
                    )
                    policy.llms.append(policy_llm)
                for piientity in policy_obj.piientities:
                    piiassoc=PIIPolicyAssociation(
                        pii_name=  piientity          
                    )
                    policy.piientities.append(piiassoc)
                for phrase in policy_obj.phrases:
                    phraseobj=BannedPhrases(
                        banned_phrase=  phrase          
                    )
                    policy.phrases.append(phraseobj)
                for region in policy_obj.geography:
                    geographyentity=PolicyGeography(
                        geography=region
                    )
                    policy.geographies.append(geographyentity)

                PromptRepository.save(session,policy_obj.prompts,modified_by,policy=policy)
                session.flush()
                session.refresh(policy)
                id=policy.id
                session.commit()                
                return [0,id] 
            except Exception as e:
                session.rollback()
                logging.error(f"an error occurred: {e}")
                raise e
            finally:
                session.close()
        

    @staticmethod
    def read(policy_id):
        with GetSession() as session:
            try:
                return session.query(Policy).options(joinedload(Policy.entities),joinedload(Policy.topics),joinedload(Policy.regexs),joinedload(Policy.metaprompts),joinedload(Policy.projects),joinedload(Policy.llms),joinedload(Policy.piientities),joinedload(Policy.phrases),joinedload(Policy.prompts),joinedload(Policy.geographies)).filter_by(id=policy_id).first()
            except Exception as e:
                raise e
            finally:
                session.close()

    @staticmethod
    async def readdetails(policy_id):
        policy= await GetPolicyDetFromCache(policy_id)
        if policy is None:
            logger.info("getting policy from database")
            with GetSession() as session:
                try:
                    policy= session.query(Policy).\
                options(joinedload(Policy.entities).subqueryload(PolicyEntityAssociation.entity),
                        joinedload(Policy.topics).subqueryload(PolicyTopicAssociation.topic),
                        joinedload(Policy.regexs).subqueryload(PolicyRegexAssociation.regex),
                        joinedload(Policy.metaprompts).subqueryload(PolicyMetapromptAssociation.metaprompt),
                        joinedload(Policy.projects).subqueryload(ProjectPolicyAssociation.project),
                        joinedload(Policy.llms).subqueryload(PolicyLLMAssociation.llm),
                        joinedload(Policy.piientities).subqueryload(PIIPolicyAssociation.piientity),
                        joinedload(Policy.phrases),
                        joinedload(Policy.prompts),
                        joinedload(Policy.geographies)).filter_by(id=policy_id).first()
                    await SetPolicyDetCache(policy_id,policy)
                    return policy
                except Exception as e:
                    raise e
                finally:
                    session.close()
        else:
            return policy
        
    @staticmethod
    def readall():
        with GetSession() as session:
            try:
                return session.query(Policy).order_by(Policy.created_on).all()
            except Exception as e:
                raise e
            finally:
                session.close()
        

    @staticmethod
    def update(policy_obj,policy_id, modified_by):
      with GetSession() as session:
        try:        
            constants=readfileAndGetData("constants")
            policy = session.query(Policy).filter_by(id=policy_id).first()
            if policy:
                if PolicyRepository.validatePolicy(session,policy_obj.name,policy_id) :
                    return 2    
                policy.policy_name=policy_obj.name
                policy.policy_desc= policy_obj.policy_desc,
                policy.industry=policy_obj.industry,  
                policy.log_level=policy_obj.log_level
                policy.code_checker=policy_obj.code_checker
                policy.anonymize=policy_obj.anonymize
                policy.block_pii="Y" if len(policy_obj.piientities)>0 else "N",  
                policy.policy_type=policy_obj.policy_type , 
                policy.injectionthreshold=policy_obj.injectionthreshold
                policy.hatefulsentimentthreshold=policy_obj.hatefulsentimentthreshold
                policy.toxicitythreshold=policy_obj.toxicitythreshold   
                policy.modified_by=modified_by
                policy.modified_on=getCurrentDateTime()     
                session.query(PolicyTopicAssociation).filter_by(
                    policy_id=policy_id).delete()
                session.query(PolicyEntityAssociation).filter_by(
                    policy_id=policy_id).delete()
                session.query(PolicyRegexAssociation).filter_by(
                    policy_id=policy_id).delete()
                session.query(PolicyMetapromptAssociation).filter_by(
                    policy_id=policy_id).delete()
                session.query(PolicyLLMAssociation).filter_by(policy_id=policy_id).delete()
                session.query(PIIPolicyAssociation).filter_by(policy_id=policy_id).delete()
                session.query(BannedPhrases).filter_by(policy_id=policy_id).delete()
                session.query(PolicyGeography).filter_by(policy_id=policy_id).delete()
                for blocked_topic in policy_obj.topics:
                    policy_topic=PolicyTopicAssociation(
                        topic_id=blocked_topic                    
                    )
                    policy.topics.append(policy_topic)
                
                for blocked_regex in policy_obj.regexs:
                    policy_regex=PolicyRegexAssociation(
                        regex_id=blocked_regex
                    
                    )
                    policy.regexs.append(policy_regex)
                
                for blocked_metaprompt in policy_obj.metaprompts:
                    policy_metaprompt = PolicyMetapromptAssociation(
                        metaprompt_id=blocked_metaprompt
                    
                    )
                    policy.metaprompts.append(policy_metaprompt)
                for blocked_entity in policy_obj.entities:
                    policy_entity=PolicyEntityAssociation(
                        entity_id=blocked_entity                  
                    )
                    policy.entities.append(policy_entity)
                for llm in policy_obj.llms:
                    policy_llm=PolicyLLMAssociation(
                        llm_id=llm                 
                    )
                    policy.llms.append(policy_llm)
                for piientity in policy_obj.piientities:
                    piiassoc=PIIPolicyAssociation(
                        pii_name=  piientity          
                    )
                    policy.piientities.append(piiassoc)
                for phrase in policy_obj.phrases:
                    phraseobj=BannedPhrases(
                        banned_phrase=  phrase          
                    )
                    policy.phrases.append(phraseobj)
                for region in policy_obj.geography:
                    geographyentity=PolicyGeography(
                        geography=region
                    )
                    policy.geographies.append(geographyentity)
                PromptRepository.save(session,policy_obj.prompts,modified_by,policy=policy)
                session.commit()
                return 0
            return 1
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def delete(policy_id):
     with GetSession() as session:
        try:
         
            policy = session.query(Policy).filter_by(id=policy_id).first()
            if policy:
                if(session.query(exists().where(ProjectPolicyAssociation.policy_id == policy_id)).scalar()):
                    return 2 #indicates Foreign Key exists 
                elif (session.query(exists().where(AppGroupAssociation.policy_id == policy_id)).scalar())  :
                    return 3     
            # all the associations to be deleted before policy gets deleted
            # Delete policy-topic associations

                session.query(PolicyTopicAssociation).filter_by(
                    policy_id=policy_id).delete()
                session.query(PolicyEntityAssociation).filter_by(
                    policy_id=policy_id).delete()
                session.query(PolicyRegexAssociation).filter_by(
                    policy_id=policy_id).delete()
                session.query(PolicyMetapromptAssociation).filter_by(
                    policy_id=policy_id).delete()
                session.query(PolicyLLMAssociation).filter_by(policy_id=policy_id).delete()
                session.query(PIIPolicyAssociation).filter_by(policy_id=policy_id).delete()
                session.query(BannedPhrases).filter_by(policy_id=policy_id).delete()
                session.query(PolicyGeography).filter_by(policy_id=policy_id).delete()
                PromptRepository.delete (session,policy_id=policy_id)  
                # Delete policy
                session.delete(policy)
                session.commit()
                return 0
            return 1
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    
    @staticmethod
    def validatePolicy(session,policy_name,policy_id):
       policy_name=policy_name.strip()
       return session.query(exists().where(and_(Policy.id != policy_id),(func.lower(Policy.policy_name)==func.lower(policy_name)))).scalar()



    @staticmethod
    def getrelatedPrompts(policy_id):
        with GetSession() as session:
            try:
                policy= session.query(Policy).filter_by(id=policy_id).first()
                topicids=[data.topic_id for data in policy.topics]
                regexids=[data.regex_id for data in policy.regexs]
                entityids=[data.entity_id for data in policy.entities]
                if len(topicids)>0 or len(regexids)>0 or len(entityids)>0:
                    return PromptRepository.getPromptsForPolicy(session,topicids,regexids,entityids)
                else:
                    return []
            except Exception as e:
                raise e
            finally:
                session.close()

    
    @staticmethod
    def getallpromptsforpolicies(session,policy_ids):
        
        policies=session.query(Policy).filter(Policy.id.in_(policy_ids)).all()
        prompts=[]
        for policy in policies:
            for prompt in policy.prompts:
                promptobj={
                    'id':prompt.id,
                    'prompt':prompt.prompt,
                    'expected_result':policy.policy_type
                }
                prompts.append(promptobj)
        return prompts
    
    @staticmethod
    def getAllLLM(session,policy_ids):
        llm_maps=session.query(PolicyLLMAssociation).options(joinedload(PolicyLLMAssociation.llm)).filter(PolicyLLMAssociation.policy_id.in_(policy_ids)).all()
        llms=[]
        for llm_map in llm_maps:
            if not llm_map.llm.llm_name in llms:
                llms.append(llm_map.llm.llm_name)
        return llms