
from util import getCurrentDateTime
from repository.promptentity import Prompts
from sqlalchemy import or_

class PromptRepository:


    @staticmethod
    def delete(session,topic_id=None,regex_id=None,entity_id=None,policy_id=None):       
        if topic_id:
          session.query(Prompts).filter_by(topic_id=topic_id).delete()
        elif regex_id:
             session.query(Prompts).filter_by(regex_id=regex_id).delete()
        elif entity_id:
            session.query(Prompts).filter_by(entity_id=entity_id).delete()
        elif policy_id:
            session.query(Prompts).filter_by(policy_id=policy_id).delete()




    @staticmethod
    def save(session,promptlist,created_by,topic=None,regex=None,entity=None,policy=None):
        allrelatedPrompts=[]
        if topic:
            allrelatedPrompts= topic.prompts
        elif regex:
            allrelatedPrompts= regex.prompts
        elif entity:
            allrelatedPrompts= entity.prompts
        elif policy:
            allrelatedPrompts=policy.prompts
        for relatedPrompt in allrelatedPrompts:
            if len([data for data in promptlist if data['id']==relatedPrompt.id])==0:
                 deletedPrompt=session.query(Prompts).filter_by(id=relatedPrompt.id).first()
                 session.delete(deletedPrompt)
        for promptdata in promptlist:
                if not promptdata['id'] or  promptdata['id']==0:
                   
                    promptentity = Prompts(
                    prompt=promptdata['prompt'],                  
                    modified_by=created_by,
                    modified_on=getCurrentDateTime(),
                    created_by=created_by,
                    created_on=getCurrentDateTime()
                )
                    if topic:
                        topic.prompts.append(promptentity)
                    elif regex:
                        regex.prompts.append(promptentity)
                    elif entity:
                        entity.prompts.append(promptentity)     
                    elif policy:
                        policy.prompts.append(promptentity)             
                else:
                   
                    promptentity = session.query(Prompts).filter_by(id=promptdata['id']).first()
                    promptentity.prompt=promptdata['prompt']
                    promptentity.modified_by=created_by,
                    promptentity.modified_on=getCurrentDateTime()
        

    @staticmethod
    def getPromptsForPolicy(session,topic_ids,regex_ids,entity_ids):
        return session.query(Prompts).filter(or_(Prompts.topic_id.in_(topic_ids),
                                                 Prompts.regex_id.in_(regex_ids),
                                                 Prompts.entity_id.in_(entity_ids))).all()
