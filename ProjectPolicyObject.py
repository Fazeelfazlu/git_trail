import datetime

class MetPromptObject:
    metapromptid:int
    metaprompt_value:int
    metaprompt_name:str
    def __init__(self,metapromptid,metaprompt_value,metaprompt_name) :
        self.metapromptid=metapromptid
        self.metaprompt_value=metaprompt_value
        self.metaprompt_name=metaprompt_name

class RegexObject:
    regex_name:str
    regex_value:str
    def __init__(self,regex_name,regex_value) :
        self.regex_name=regex_name
        self.regex_value=regex_value

class LLmObject:
    llm:str
    watermark_text:str
    def __init__(self,llm,watermark_text) :
        self.llm=llm
        self.watermark_text=watermark_text

class PIIObject:
    pii_name:str
    pii_desc:str
    def __init__(self,pii_name,pii_desc) :
        self.pii_name=pii_name
        self.pii_desc=pii_desc

class PolicyObject:
    id:int
    policy_name:str
    llms:list[LLmObject]
    block_pii:str
    code_checker:str
    anonymize:str
    topics:list[str]
    regexs:list[RegexObject]
    entities:list[str]
    metaprompts:list[MetPromptObject]
    policy_type:str
    log_level:str
    pii_names:list[PIIObject]
    banned_phrases:list[str]
    injectionthreshold:float
    hatefulsentimentthreshold:float
    toxicitythreshold:float
    def __init__(self,id,policy_name,llms,block_pii,code_checker,anonymize,topics,regexs,entities,metaprompts,policy_type,log_level,pii_names,banned_phrases,injectionthreshold,hatefulsentimentthreshold,toxicitythreshold):
        self.id=id
        self.policy_name=policy_name
        self.llms=llms
        self.block_pii=block_pii
        self.code_checker=code_checker
        self.anonymize=anonymize
        self.topics=topics
        self.regexs=regexs
        self.entities=entities
        self.metaprompts=metaprompts
        self.policy_type=policy_type
        self.log_level=log_level
        self.pii_names=pii_names
        self.banned_phrases=banned_phrases
        self.injectionthreshold=injectionthreshold
        self.hatefulsentimentthreshold=hatefulsentimentthreshold
        self.toxicitythreshold=toxicitythreshold




class ProjectPolicyObject:
    id:str
    project_name:str
    policies:list[PolicyObject]
    project_desc  : str
    app_ci: str
    app_url: str
    owner_name: str
    owner_handle: str
    owner_email: str
    approver_name: str
    approver_handle: str
    approver_email: str
    from_date:datetime 
    to_date:datetime 
    locked: str
    active: str
    topics:list[str]
    def __init__(self,id,project_name,policies,project_desc,app_ci,app_url,owner_name,owner_handle,owner_email,
                 approver_name,approver_handle,approver_email,from_date,to_date,locked,active,topics):
        self.id=id
        self.project_name=project_name
        self.policies=policies
        self.project_desc=project_desc
        self.app_ci=app_ci
        self.app_url=app_url
        self.owner_name=owner_name
        self.owner_handle=owner_handle
        self.owner_email=owner_email
        self.approver_name=approver_name
        self.approver_handle=approver_handle
        self.approver_email=approver_email
        self.from_date=from_date
        self.to_date=to_date
        self.locked=locked
        self.active=active
        self.topics=topics