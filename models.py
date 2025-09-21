from fastapi import FastAPI
from pydantic import BaseModel,Field
from typing import Any, Optional
from json import JSONEncoder

class AuthenticationModel(BaseModel):
    username : str = Field(max_length=300)
    password : str = Field(max_length=200)

class ValidateUsernameModel(BaseModel):
    username : str = Field(max_length=300)

class ResetPasswordModel(BaseModel):
    username : str = Field(max_length=300)
    code : str = Field(max_length=6)
    password : str = Field(max_length=200)

class UpdateTopicModel(BaseModel):
    topic_name : str = Field(max_length=40)
    topic_desc : str = Field(max_length=2000)
    prompts : list 

class UpdateEntityModel(BaseModel):
    type : str  
    annotations : list
    classes : list

class GetTrainingEntitiesModel(BaseModel):
    trainingtype : str = Field(max_length=1)

class UpdateEntityDetailsModel(BaseModel):
    entity_desc : str = Field(max_length=2000)
    prompts : list

class UpdateRegexModel(BaseModel):
    name : str = Field(max_length=50)
    pattern : str = Field(max_length=200)
    regex_desc : str = Field(max_length=2000)
    prompts : list

class SaveApprovalflowModel(BaseModel):
    Value : str
    
class UpdateMetapromptModel(BaseModel):
    name : str = Field(max_length=50)
    prompt : str = Field(max_length=2000)
    metaprompt_desc : str = Field(max_length=2000)
    
class TrainedOnModel(BaseModel):
    id : int
    datasetname : str = Field(max_length=200)
    data_url : str = Field(max_length=500)
    version : str = Field(max_length=50)
    remarks : str = Field(max_length=2000)

class UpdateLLMModel(BaseModel):
    name : str = Field(max_length=200)
    family_name : str = Field(max_length=200)
    watermark_text : str = Field(max_length=2000)
    llm_remarks : str = Field(max_length=2000)
    llm_url : str = Field(max_length=500)
    license_type : str = Field(max_length=200)
    llm_desc : str = Field(max_length=2000)
    trainedOn : list[TrainedOnModel]

class UpdatePolicyModel(BaseModel):
    name : str = Field(max_length=100)
    policy_desc : str = Field(max_length=2000)
    industry : str = Field(max_length=100)
    log_level : str = Field(max_length=50)
    code_checker : str = Field(max_length=1)
    anonymize : str = Field(max_length=1)
    piientities : list
    policy_type : str = Field(max_length=20)
    injectionthreshold : float
    hatefulsentimentthreshold : float
    toxicitythreshold : float        
    topics : list
    geography: list
    block_pii: str = Field(max_length=1)
    regexs: list
    metaprompts: list
    entities: list
    llms: list
    piientities: list
    phrases: list
    prompts: list

class UpdateUserModel(BaseModel):
    firstname : str = Field(max_length=100)
    lastname : str = Field(max_length=100)
    user_role : str = Field(max_length=50)

class CreateUserModel(BaseModel):
    username : str = Field(max_length=300)
    firstname : str = Field(max_length=100)
    lastname : str = Field(max_length=100)
    user_role : str = Field(max_length=50)
    
class ChangePasswordModel(BaseModel):
    oldpassword : str = Field(max_length=200)
    newpassword : str = Field(max_length=200)
    
class GetUserFromHandelModel(BaseModel):
    username : str = Field(max_length=300)
    
class VerifyOTPModel(BaseModel):
    username : str = Field(max_length=300)
    code : str = Field(max_length=6)
    
class CreateAppgroupModel(BaseModel):
    name : str = Field(max_length=100)
    desc : str = Field(max_length=2000)
    policies : list

class CreateProjectModel(BaseModel):
    name : str = Field(max_length=100)
    appgroup_id : Optional[int]
    project_desc : str = Field(max_length=2000)
    app_ci : str = Field(max_length=100)
    app_url : Optional[str] = Field(max_length=500)
    owner_name : Optional[str] = Field(max_length=500)
    owner_handle : Optional[str] = Field(max_length=100)
    owner_email : Optional[str] = Field(max_length=200)
    approver_name : Optional[str] = Field(max_length=500)
    approver_handle : Optional[str] = Field(max_length=100)
    approver_email : Optional[str] = Field(max_length=200)
    from_date : str
    to_date : str
    locked : str = Field(max_length=1)
    active : str = Field(max_length=1)
    policies : list
    
class RunTuringPromptModel(BaseModel):
    prompt : str = Field(max_length=2000)
    llm : str = Field(max_length=200)

class GuardrailProjconfig(BaseModel):
    key : str 
    name : str

class GuardrailContexModel(BaseModel):
    llm : str = Field(max_length=200)
    username : str = Field(max_length=200)
    hostname : str = Field(max_length=500)
    ip : str = Field(max_length=50)
    israg : Optional[str]
    isChat : Optional[str]

class GuardrailModel(BaseModel):
    projconfig : GuardrailProjconfig
    prompt : str = Field(max_length=4000)
    context : GuardrailContexModel
    invocation_id : str = Field(max_length=100)
    invocation_type : str = Field(max_length=20)

class AnonymizeContextModel(BaseModel):
    username : str = Field(max_length=200)
    llm : str = Field(max_length=200)
    ip : str = Field(max_length=50)
    hostname : str = Field(max_length=500)

class AnonymizeModel(BaseModel):
    projconfig : GuardrailProjconfig
    chunks : list
    context : AnonymizeContextModel
    invocation_id : str = Field(max_length=100)
    invocation_type : str = Field(max_length=20)

class DeanonymizeModel(BaseModel):
    projconfig : GuardrailProjconfig
    text : str = Field(max_length=2000)
    context : AnonymizeContextModel
    invocation_id : str = Field(max_length=100)
    invocation_type : str = Field(max_length=20)
    
class UserSettingModel(BaseModel):
    settingname : str = Field(max_length=50)
    settingvalue : str = Field(max_length=50)
    
class DefaultJSONEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        return o.__dict__
    
    
    


    
