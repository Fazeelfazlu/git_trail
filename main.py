from fastapi import Request,UploadFile
from fastapi.responses import JSONResponse,StreamingResponse,FileResponse
import json
import uvicorn
from models import *

from create_app import app,config_data

import os
from werkzeug.exceptions import HTTPException
from logger import logger
from util import getCurrentDateTime,getFormattedDateTime,getFormattedDateTimeWithoutTimeZone,encryptPass
from datareader import readfileAndGetData
import jwt
from repository.promptrepository import PromptRepository
from repository.topicrepository import TopicRepository
from repository.regexrepository import RegexRepository
from repository.metapromptrepository import MetapromptRepository
from repository.entityrepository import EntityRepository
from repository.policyrepository import PolicyRepository
from repository.llmrepository import LLMRepository
from repository.projectrepository import ProjectRepository
from repository.userrepository import UserRepository
from repository.piirepository import PIIRepository
from repository.trainingstatusrepository import TrainingStatusRepository
from repository.appgrouprepository import AppgroupRepository
from repository.versionrepository import VersionRepository
from checkauth import isAuthenticated,AutheticateTuringPrompt,getuserrole
from filegenerator import GenerateConfigFile,GenerateExportFile,GetImportedFileData,GenerateTextFile,ExportModelFile,CheckModelExists,ExtractModelFile,CopyModel,DeleteExtractedFile
from guardrailmanager import RunGuardRail,Anonymize,DeAnonymize,GeneratePseudoUserName
from guardrailmanager import ReturnUserName
import numpy as np
import time
from urllib import parse
from plugins.TopicsChekcer import TopicsChecker
from repository.policyviolationrepository import PolicyViolationRepository
from repository.projectpolicydetailsrepository import ProjectPolicyDetailsRepository
from repository.CacheManager import ClearProjectCache
import datetime
from keyvaultmanager import getKeyVaultSecret
from otpmanager import OTPManager
from RoleManager import RoleMapping
from RoleAccess import RoleAccess
from repository.AppSettingsRepository import AppSettingsRepository


arrToxicity=[{
    "score":0.4,"desc":"High"
},{
    "score":0.5,"desc":"Medium High"
},{
    "score":0.6,"desc":"Medium"
},{
    "score":0.7,"desc":"Medium Low"
},{
    "score":0.8,"desc":"Low"
}
]
arrNegativity=[{
    "score":-0.2,"desc":"High"
},{
    "score":-0.3,"desc":"Medium High"
},{
    "score":-0.4,"desc":"Medium"
},{
    "score":-0.5,"desc":"Medium Low"
},{
    "score":-0.6,"desc":"Low"
}
]

#apiRunning
@app.route("/")
def index(request : Request):
    logger.info("This is a test login")
    return JSONResponse(content="API is running.", status_code=200 )

#region Dashboard API
@app.get("/getdashboarddata/{projectid}/{policyid}")
def GetPolicyViolations(projectid : str, policyid: int,request: Request,startdate :str,enddate:str ):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    
    policviolationlist=PolicyViolationRepository.readviolations(projectid,policyid,startdate,enddate)
    serialized_polviolations = []
    for violation in policviolationlist:
        serialized_violation = {
            'project_id': violation.project_id,
            'policy_id': violation.policy_id,
            'invocation_id':violation.invocation_id,
            'invocation_type': violation.invocation_type,
            'violation_type': violation.violation_type,
            'violation_field_value': violation.violation_field_value,
            'policy_type': violation.policy_type,
            'log_level': violation.log_level,
            'created_on': getFormattedDateTime(violation.created_on),  # Convert datetime to string          
            'created_by': violation.created_by
        }
        serialized_polviolations.append(serialized_violation)
    return JSONResponse(content=serialized_polviolations, status_code=200 )


#endregion

#region Topic
@app.get("/gettopics")
def GetTopics(request: Request):
    
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    
    topics = TopicRepository.readall()
    serialized_topics = []
    for topic in topics:
        prompts=[]
        for promptdata in topic.prompts:
            promptObj={
                'id':promptdata.id,
                'prompt':promptdata.prompt
            }
            prompts.append(promptObj)
        serialized_topic = {
            'id': topic.id,
            'topic_name': topic.topic_name,
            'topic_desc':topic.topic_desc if topic.topic_desc and not topic.topic_desc==None else "",
            'modified_by': topic.modified_by,
            'modified_on': getFormattedDateTime(topic.modified_on),  # Convert datetime to string
            'created_on': getFormattedDateTime(topic.created_on),  # Convert datetime to string
            'created_by': topic.created_by,
            'prompts':prompts
        }
        serialized_topics.append(serialized_topic)
    return JSONResponse(content=serialized_topics, status_code=200 )


@app.post("/updatetopic/{id}")
async def UpdateTopic(id:int,updateTopicReq:UpdateTopicModel,request:Request):
    username = isAuthenticated(request)
    if username is None:
        return UnauthenticatedUserResponseReturn()

    # call repository
    try:
        # req_body = request
        topic_name = updateTopicReq.topic_name
        topic_desc = updateTopicReq.topic_desc
        prompts = updateTopicReq.prompts
        result=TopicRepository.update(topic_name,topic_desc,prompts,id, username)
        if result==0:
            inittopcchecker()
            await ClearProjectCache()
            return JSONResponse(content={"message":  "Topic updated successfully."}, status_code=200)
        elif result==1:
             return JSONResponse(content={"message":   "Topic doesn't exist."},status_code=500)
        elif result==2:
            return JSONResponse(content={"message":   "Duplicate Topic exists."},status_code=500)
    except Exception as e:
        logger.error(f"Topic Update failed {e}")
        return JSONResponse(content={"message":   "Update failed!"}, status_code=500)
    
    
@app.post("/createtopic")
def CreateTopic(updateTopicReq:UpdateTopicModel,request:Request):
    username = isAuthenticated(request)
    if username is None:
         return UnauthenticatedUserResponseReturn() 
    # call repository
    try:
        # req_body = request.json
        topic_name = updateTopicReq.topic_name
        topic_desc = updateTopicReq.topic_desc
        prompts = updateTopicReq.prompts
        result= TopicRepository.create(topic_name,topic_desc,prompts, username)
        if result==0:
            inittopcchecker()
            return JSONResponse(content={"message":   "Topic created successfully."}, status_code=200)
        elif result==1:
            return JSONResponse(content={"message":   "Topic doesnt exist."}, status_code=500)
        elif result==2:
            return JSONResponse(content={"message":   "Duplicate Topic exists."}, status_code=500)
    except Exception as e:
        logger.error(f"Topic Creation failed {e}")
        return JSONResponse(content={"message":   "Topic creation failed!"}, status_code=500)

@app.delete("/deletetopic/{id}")
def DeleteTopic(id:int,request:Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    # call repository
    try:
        
        result= TopicRepository.delete(id)
        if result==0:
            inittopcchecker()
            return JSONResponse(content={"message": "Topic deleted successfully."}, status_code=200)
        elif result==1:
            return JSONResponse(content={"message": "Topic doesnt exist."}, status_code=500)
        elif result==2:
            return JSONResponse(content={"message": "Topic cannot be deleted as it is linked to policy."}, status_code=500)
    except Exception as e:
        logger.error(f"Topic Deletion failed {e}")
        return JSONResponse(content={"message": "Topic deletion failed!"}, status_code=500)

#endregion

#region Init Topic Checker
def inittopcchecker():
    topicsList=TopicRepository.readall()
    topicsList=[data.topic_name for data in topicsList]
    topicsList.append("General")
    TopicsChecker.inittopics(topicsList)  

inittopcchecker()

#endregion
  
#region Regex
@app.get("/getregex")
def GetRegex(request: Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    
    regexlist = RegexRepository.readall()
    serialized_regexs = []
    for regex in regexlist:
        prompts=[]
        for promptdata in regex.prompts:
            promptObj={
                'id':promptdata.id,
                'prompt':promptdata.prompt
            }
            prompts.append(promptObj)
        serialized_regex = {
            'id': regex.id,
            'name': regex.regex_name,
            'pattern':regex.regex_value,
             'regex_desc':regex.regex_desc,
            'modified_by': regex.modified_by,
            'modified_on': getFormattedDateTime(regex.modified_on),  # Convert datetime to string
            'created_on': getFormattedDateTime(regex.created_on),  # Convert datetime to string
            'created_by': regex.created_by,
            'prompts':prompts
        }
        serialized_regexs.append(serialized_regex)
    return JSONResponse(content=serialized_regexs, status_code=200)


@app.post("/updateregex/{id}")
async def UpdateRegex(id:int,updateRegexReq:UpdateRegexModel,request:Request):
    username = isAuthenticated(request)
    if username is None:
        return UnauthenticatedUserResponseReturn()

    # call repository
    try:
        name = updateRegexReq.name
        pattern = updateRegexReq.pattern
        regex_desc = updateRegexReq.regex_desc
        prompts = updateRegexReq.prompts
       
        result=RegexRepository.update(id,name,pattern,regex_desc,prompts, username)
        if result==0:
            await ClearProjectCache()
            return JSONResponse(content={"message": "Regex updated successfully."}, status_code=200)
        elif result==1:
            return JSONResponse(content={"message": "Regex doesnt exist."}, status_code=500)
        elif result==2:
            return JSONResponse(content={"message": "Duplicate Regex Name exists."}, status_code=500)
    except Exception as e:
        logger.error(f"Regex Update failed {e}")
        return JSONResponse(content={"message": "Regex Update failed!"}, status_code=500)


@app.post("/createregex")
def CreateRegex(updateRegexReq:UpdateRegexModel,request:Request):
    username = isAuthenticated(request)
    if username is None:
         return UnauthenticatedUserResponseReturn() 
    # call repository
    try:
        name = updateRegexReq.name
        pattern = updateRegexReq.pattern
        regex_desc = updateRegexReq.regex_desc
        prompts = updateRegexReq.prompts
        result=RegexRepository.create(name,pattern,regex_desc,prompts,username)
        if result==0:
            return JSONResponse(content={"message": "Regex created successfully."}, status_code=200)
        elif result==1:
            return JSONResponse(content={"message": "Regex doesnt exist."}, status_code=500)
        elif result==2:
            return JSONResponse(content={"message": "Duplicate Regex Name exists."}, status_code=500)
    except Exception as e:
        logger.error(f"Regex creation failed {e}")
        return JSONResponse(content={"message": "Regex creation failed!"}, status_code=500)


@app.delete("/deleteregex/{id}")
def DeleteRegex(id:int,request:Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    # call repository
    try:
       
       
        result= RegexRepository.delete(id)
        if result==0:
            return JSONResponse(content={"message": "Regex deleted successfully."}, status_code=200)
            return Response(
                json.dumps()          ,
                status=200,
                mimetype="application/json" 
            )
        elif result==1:
            return JSONResponse(content={"message": "Regex doesnt exist."}, status_code=500)
        elif result==2:
            return JSONResponse(content={"message": "Regex cannot be deleted as it is linked to policy."}, status_code=500)
    except Exception as e:
        logger.error(f"Regex Deletion failed {e}")
        return JSONResponse(content={"message": "Regex deletion failed!"}, status_code=500)

#endregion

#region Metaprompt
@app.get("/getmetaprompt")
def Getmetaprompt(request: Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    metapromptlist = MetapromptRepository.readall()
    serialized_metaprompts = []
    for metaprompt in metapromptlist:
        serialized_metaprompt = {
            'id': metaprompt.id,
            'name': metaprompt.metaprompt_name,
            'prompt':metaprompt.metaprompt_value,
            'metaprompt_desc':metaprompt.metaprompt_desc,
            'modified_by': metaprompt.modified_by,
            'modified_on': getFormattedDateTime(metaprompt.modified_on),  # Convert datetime to string
            'created_on': getFormattedDateTime(metaprompt.created_on),  # Convert datetime to string
            'created_by': metaprompt.created_by
        }
        serialized_metaprompts.append(serialized_metaprompt)
    return JSONResponse(content=serialized_metaprompts, status_code=200)


@app.post("/createmetaprompt")
def CreateMetaprompt(updateMetapromptReq : UpdateMetapromptModel, request : Request):
    username = isAuthenticated(request)
    if username is None:
         return UnauthenticatedUserResponseReturn() 
    # call repository
    try:
        name = updateMetapromptReq.name
        prompt = updateMetapromptReq.prompt
        metaprompt_desc = updateMetapromptReq.metaprompt_desc
        result=MetapromptRepository.create(name,prompt,metaprompt_desc, username)
        if result==0:
            return JSONResponse(content={"message": "Metaprompt created successfully."}, status_code=200)
        elif result==1:
            return JSONResponse(content={"message": "Metaprompt doesnt exists."}, status_code=500)
        elif result==2:
            return JSONResponse(content={"message": "Duplicate Metaprompt name exists."}, status_code=500)
    except Exception as e:
        logger.error(f"Metaprompt creation failed {e}")
        return JSONResponse(content={"message": "Metaprompt creation failed!"}, status_code=500)


@app.post("/updatemetaprompt/{id}")
async def UpdateMetaprompt(id:int,updateMetapromptReq : UpdateMetapromptModel,request:Request):
    username = isAuthenticated(request)
    if username is None:
        return UnauthenticatedUserResponseReturn()
    # call repository
    try:
        name = updateMetapromptReq.name
        prompt = updateMetapromptReq.prompt
        metaprompt_desc = updateMetapromptReq.metaprompt_desc
        result=MetapromptRepository.update(id,name,prompt,metaprompt_desc,username)
        if result==0:
            await ClearProjectCache()
            return JSONResponse(content={"message": "Metaprompt updated successfully."}, status_code=200)
        elif result==1:
            return JSONResponse(content={"message": "Metaprompt doesnt exists."}, status_code=500)
        elif result==2:
            return JSONResponse(content={"message": "Duplicate Metaprompt name exists."}, status_code=500)
    except Exception as e:
        logger.error(f"Metaprompt update failed {e}")
        return JSONResponse(content={"message": "Metaprompt update failed!"}, status_code=500)

@app.delete("/deletemetaprompt/{id}")
def DeleteMetaprompt(id:int,request:Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    # call repository
    try:
        result=MetapromptRepository.delete(id)
        if result==0:
            return JSONResponse(content={"message": "Metaprompt deleted successfully."}, status_code=200)
        elif result==1:
            return JSONResponse(content={"message": "Metaprompt doesnt exist."}, status_code=500)
        elif result==2:
            return JSONResponse(content={"message": "Metaprompt cannot be deleted as it is linked to policy."}, status_code=500)
    except Exception as e:
        logger.error(f"Metaprompt Deletion failed {e}")
        return JSONResponse(content={"message":   "Metaprompt deletion failed!"}, status_code=500)
#endregion
   
#region LLM
@app.get("/getllms")
def GetLLMs(request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()    
    llms = LLMRepository.readall()
    serialized_llms = []
    for llm in llms:
        trainedOn=[]
        for datatrained in llm.trainedOn:
            data={
                'id':datatrained.id,
                'datasetname':datatrained.datasetname,
                'data_url':datatrained.data_url if datatrained.data_url!=None else "",
                'version':datatrained.version if datatrained.version!=None else "",
                'remarks':datatrained.remarks if datatrained.remarks!=None else "",
                'modified_by': datatrained.modified_by,
                'modified_on': getFormattedDateTime(datatrained.modified_on),  # Convert datetime to string
                'created_on': getFormattedDateTime(datatrained.created_on),  # Convert datetime to string
                'created_by': datatrained.created_by
            }
            trainedOn.append(data)
        serialized_llm = {
            'id': llm.id,
            'name': llm.llm_name,
            'family_name':llm.llm_family_name,
            'watermark_text':llm.watermark_text,
            'llm_remarks':llm.llm_remarks if llm.llm_remarks!=None else "",
            'llm_url':llm.llm_url if llm.llm_url!=None else "",
            'license_type':llm.license_type if llm.license_type!=None else "",
            'llm_desc':llm.llm_desc,
            'modified_by': llm.modified_by,
            'modified_on': getFormattedDateTime(llm.modified_on),  # Convert datetime to string
            'created_on': getFormattedDateTime(llm.created_on),  # Convert datetime to string
            'created_by': llm.created_by,
            'trainedOn':trainedOn
        }
        serialized_llms.append(serialized_llm)
    return JSONResponse(content=serialized_llms, status_code=200)

@app.post("/updatellm/{id}")
async def UpdateLLM(id:int, updateLLMReq : UpdateLLMModel,request:Request):
    username = isAuthenticated(request)
    if username is None:
        return UnauthenticatedUserResponseReturn()

    # call repository
    try:     
        result=LLMRepository.update(updateLLMReq,id, username)
        if result==0:
            await ClearProjectCache()
            return JSONResponse(content={"message": "LLM updated successfully."}, status_code=200)
        elif result==1:
            return JSONResponse(content={"message": "LLM doesnt exists."}, status_code=500)
        elif result==2:
            return JSONResponse(content={"message": "Duplicate LLM Name exists."}, status_code=500)
    except Exception as e:
        logger.error(f"LLM Update failed {e}")
        return JSONResponse(content={"message": "LLM Update failed!"}, status_code=500)

@app.post("/createllm")
def CreateLLM(updateLLMReq : UpdateLLMModel,request:Request):
    username = isAuthenticated(request)
    if username is None:
         return UnauthenticatedUserResponseReturn() 
    # call repository
    try:
        
        result=LLMRepository.create(updateLLMReq, username)
        if result==0:
            return JSONResponse(content={"message": "LLM created successfully."}, status_code=200)
        elif result==1:
            return JSONResponse(content={"message": "LLM doesnt exists."}, status_code=500)
        elif result==2:
            return JSONResponse(content={"message": "Duplicate LLM Name exists."}, status_code=500)
    except Exception as e:
        logger.error(f"LLM creation failed {e}")
        return JSONResponse(content={"message": "LLM creatation failed!"}, status_code=500)

@app.delete("/deletellm/{id}")
def DeleteLLM(id : int, request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    # call repository
    try:
       
        result=LLMRepository.delete(id)
        if result==0:
            return JSONResponse(content={"message": "LLM deleted successfully."}, status_code=200)
        elif result==1:
            return JSONResponse(content={"message": "LLM doesnt exists."}, status_code=500)
        elif result==2:
            return JSONResponse(content={"message": "LLM cannot be deleted as it is linked to policy."}, status_code=500)
    except Exception as e:
        logger.error(f"LLM Deletion failed {e}")
        return JSONResponse(content={"message": "LLM deletion failed!"}, status_code=500)

#endregion

#region Entity
@app.get("/getentitites")
def GetEntitites(request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    
    entitytraininglist = EntityRepository.readall()
    training_status=TrainingStatusRepository.GetEntityStatus()
    serialized_entitites = []
    for entity in entitytraininglist:
        jsonData=json.loads(entity.entitytraining_json)
        annotations=jsonData["annotations"]
        firstLine=""
        if len(annotations)> 0 and len(annotations[0])>0:
            length=1000 if len(annotations[0][0])>1000 else len(annotations[0][0])
            firstLine=annotations[0][0][:length]+ "..."
        
        serialized_entity = {
            'id': entity.id,
            'datatext':firstLine,
            'istrained':entity.istrained,
            'trainingtype':entity.trainingtype,
            'entities': [data.entity.entity_value for data in entity.entitites if data.entity],           
            'modified_by': entity.modified_by,
            'modified_on': getFormattedDateTime(entity.modified_on),  # Convert datetime to string
            'created_on': getFormattedDateTime(entity.created_on),  # Convert datetime to string
            'created_by': entity.created_by
        }
        serialized_entitites.append(serialized_entity)
    responseobj={
        "entities":serialized_entitites,
        "status":training_status.training_status,
        "model_date":getFormattedDateTime(training_status.last_successful_training_on) if training_status.last_successful_training_on else "",
        "f1-score":round(float(training_status.f1_score*100),2) if training_status.f1_score else ""

    }
    return JSONResponse(content=responseobj, status_code=200)

@app.get("/getentity/{id}")
def GetEntitity(id : int, request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
   
    entity = EntityRepository.read(id)
    trainingJson=entity.entitytraining_json
    serialized_entity={
        'training_json':trainingJson,
        'type':entity.trainingtype
    }
    return JSONResponse(content=serialized_entity, status_code=200)    

@app.post("/updateentity/{id}")
async def UpdateEntity(id : int, updateEntityReq : UpdateEntityModel, request : Request):
    username = isAuthenticated(request)
    if username is None:
        return UnauthenticatedUserResponseReturn()

    # call repository
    try:
        EntityRepository.update(updateEntityReq,id, username)
        await ClearProjectCache()
        return JSONResponse(content={"message":  "Entity updated successfully."}, status_code=200)
    except ValueError as e:
        logger.error(e)
        return JSONResponse(content={"message": "Entity Update failed!"}, status_code=200)
 
@app.post("/createentity")
def CreateEntity(updateEntityReq : UpdateEntityModel, request : Request):
    username = isAuthenticated(request)
    if username is None:
         return UnauthenticatedUserResponseReturn() 
    # call repository
    # try:
    
    EntityRepository.create(updateEntityReq, username)
    return JSONResponse(content={"message": "Entity created successfully."}, status_code=200)
    # except ValueError as ex:
        # return Response(
        #     json.dumps({"message":   "Entity creation failed!"})    ,
        #     status=500
        # )

@app.get("/gettrainingentitites")
def GetTrainingEntitites(traingEntitiesReq : GetTrainingEntitiesModel , request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    trainingtype=traingEntitiesReq.trainingtype
    if trainingtype not in ['T','V']:
        return JSONResponse(content={"message": "Proper Training type not specified."}, status_code=500)
    entitylist = EntityRepository.readalltraining(trainingtype)
    classes=np.array([])
    annotations=[]
    for entity in entitylist:
        trainingJSon=json.loads(entity.entitytraining_json)
        classList=np.array(trainingJSon["classes"])
        classes=np.append(classes,classList)
        annotationsList=trainingJSon["annotations"]
        for annotationObj in annotationsList:    
            annotations.append(annotationObj)
       
    return JSONResponse(content={'classes':classes.tolist(),'annotations':annotations}, status_code=200)

@app.get("/validatedelete/{entity_name}")
def ValidateDelete(entity_name : int, request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    result=EntityRepository.validateDeletion(entity_name)
    if not result:
        result=False
    return JSONResponse(content={"result":   result}, status_code=200)

@app.post("/train")    
def train(request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    try:        
        TrainingStatusRepository.initiatetraining(username)  
        return JSONResponse(content={"message":"Model training initiated successfully."}, status_code=200) 
    except Exception as e:
        logger.error(f"trining failed {e}")
        return JSONResponse(content={"message":"Model training failed!"}, status_code=500)

@app.get("/gettrainingstatus")
def GetTrainingStatus(request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()    
 
    training_status=TrainingStatusRepository.GetEntityStatus()  
    constants= readfileAndGetData("constants") 
    isModelExisits=CheckModelExists(constants["FILE_PATHS"]["MODELFILE"])
    logger.info(f"Time 5 {training_status.last_successful_training_on}")
    responseobj={       
        "status":training_status.training_status,
        "model_date":getFormattedDateTime(training_status.last_successful_training_on) if training_status.last_successful_training_on else "",
        "f1-score":round(float(training_status.f1_score*100),2) if training_status.f1_score else "",
        "isModelExists":"Y" if isModelExisits==1 else "N",
        "model_source":training_status.model_source

    }
    return JSONResponse(content=responseobj, status_code=200)

@app.get("/getallentitites")
def GetAllEntitites(request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    
    entitylist = EntityRepository.readallEntity()    
    serialized_entitites = []
    for entity in entitylist:
        prompts=[]
        for promptdata in entity.prompts:
            promptObj={
                'id':promptdata.id,
                'prompt':promptdata.prompt
            }
            prompts.append(promptObj)
        serialized_entity = {
            'id': entity.id,
            'entity_value':entity.entity_value,   
            'entity_desc':entity.entity_desc,              
            'modified_by': entity.modified_by,
            'modified_on': getFormattedDateTime(entity.modified_on),  # Convert datetime to string
            'created_on': getFormattedDateTime(entity.created_on),  # Convert datetime to string
            'created_by': entity.created_by,
            'prompts':prompts
        }
        serialized_entitites.append(serialized_entity)
    return JSONResponse(content=serialized_entitites, status_code=200)

@app.post("/updateentitydetails/{id}")
async def UpdateEntityDetails(id : int, entityDetailsReq : UpdateEntityDetailsModel, request : Request):
    username = isAuthenticated(request)
    if username is None:
        return UnauthenticatedUserResponseReturn()

    # call repository
    try:      
        EntityRepository.updateEntityDetails(id,entityDetailsReq,username)
        await ClearProjectCache()
        return JSONResponse(content={"message": "Entity updated successfully."}, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": "Entity Update failed!"}, status_code=500)

@app.delete("/deleteentity/{id}")
async def DeleteEntity(id : int, request : Request):
    username = isAuthenticated(request)
    if username is None:
        return UnauthenticatedUserResponseReturn()
    # call repository
    try:
        EntityRepository.delete(id)
        await ClearProjectCache()
        return JSONResponse(content={"message": "Entity deleted successfully."}, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": "Entity deletion failed!"}, status_code=500)

@app.get("/downloadtext/{id}")
def DownloadEntityText(id : int, request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
   
    entity = EntityRepository.read(id)
    if not entity:
        return JSONResponse(content={"message": "Entity doesn't exists for requested ID"})
    trainingJson=entity.entitytraining_json
    jsondata=json.loads(trainingJson)   
    annotations=  [data[0] for data in jsondata['annotations'] ]
    fullText="\n".join(annotations)
    return StreamingResponse(GenerateTextFile(fullText), media_type="application/octet-stream")

@app.get("/exportmodel")
def ExportModel(request:Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
   
    trainingStatus = TrainingStatusRepository.GetEntityStatus()
    constants= readfileAndGetData("constants") 
    modelPath=constants["FILE_PATHS"]["MODELFILE"]
    statusFilePath=constants["FILE_PATHS"]["STATUSFILENAME"]
    zipFilePath=constants["FILE_PATHS"]["ZIPFILEPATH"]

    statusData={
        'status':trainingStatus.training_status,
        'score':round(float(trainingStatus.f1_score*100),2) if trainingStatus.f1_score else "",
        'run_date':getFormattedDateTime(trainingStatus.last_successful_training_on),
         'env':config_data["ENV"]     
    }
    return StreamingResponse(ExportModelFile(statusData,modelPath,statusFilePath,zipFilePath), media_type="application/octet-stream")
    
@app.post("/importmodel")
def ImportModel(file: UploadFile, request : Request):
     username = isAuthenticated(request)
     if username is None:
       return UnauthenticatedUserResponseReturn()
     try:
        if not file:
            return JSONResponse(content={'message':'File not found.'}, status_code=500)
        else:
            
            filetype = os.path.splitext(file.filename)[-1]
            if not filetype == ".zip":
                logger.info(f"File type not supported")
                return JSONResponse(content={"message":"File type not supported."}, status_code=500)
            
            file = file.file
            size =  request.headers.get("Content-Length")
            if int(size) > config_data["MODEL_FILE_SIZE"]:
                logger.info(f"File size exceeded while uploading project.")
                return JSONResponse(content={"message":"File size exceeded."}, status_code=500)
        
            constants= readfileAndGetData("constants") 
            modelPath=constants["FILE_PATHS"]["MODELFILE"]
            statusFilePath=constants["FILE_PATHS"]["STATUSFILENAME"]
            result=ExtractModelFile(file,modelPath,statusFilePath)
            if result[0]==0:
                trainingStatus=result[1]
                result =TrainingStatusRepository.ImportModelData(trainingStatus)
                if result==0:
                    CopyModel(modelPath) 
                    return JSONResponse(content={"message": "Model imported successfully."}, status_code=200)              
            elif result[0]==1:
                return JSONResponse(content={"message": "Imported model not in proper format."}, status_code=500)
     except Exception as e:
        logger.error(f"Error in Importing Model {e}")
        return JSONResponse(content={"message": "Imported model not in proper format."}, status_code=500)
     finally:
         constants= readfileAndGetData("constants") 
         modelPath=constants["FILE_PATHS"]["MODELFILE"]
         DeleteExtractedFile(modelPath)
         
#endregion

#region Policy

@app.get("/getpolicies")
def GetPolicies(request : Request):
    username = isAuthenticated(request)
    startime=startime=time.time()  
    if username is None:
       return UnauthenticatedUserResponseReturn()
    policylist = PolicyRepository.readall()
    logger.info(f"DB Get time { time.time()-startime }")
    serialized_Policies = []
    for policy in policylist:
     
        serialized_policy = {
            'id': policy.id,
            'name':policy.policy_name,
            'policy_desc':policy.policy_desc,
            'industry':policy.industry,            
            'log_level':policy.log_level,
            'code_checker': policy.code_checker,      
            'anonymize': policy.anonymize,  
            'block_pii':policy.block_pii,
            'policy_type':policy.policy_type,
            'modified_by': policy.modified_by,
            'modified_on': getFormattedDateTime(policy.modified_on),  # Convert datetime to string
            'created_on': getFormattedDateTime(policy.created_on),  # Convert datetime to string
            'created_by': policy.created_by
        }
        serialized_Policies.append(serialized_policy)
    logger.info(f"Finish TIme { time.time()-startime }")
    return JSONResponse(content=serialized_Policies, status_code=200)

@app.get("/getpolicydetails/{id}")
async def GetPolicyDetails(id : int, request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
   
    policy = await PolicyRepository.readdetails(id)
    prompts=[]
    for prompt in policy.prompts:
        objprompt={
            'id':prompt.id,
            'prompt':prompt.prompt
        }
        prompts.append(objprompt)
    serialized_policy = {
            'id': policy.id,
            'name':policy.policy_name,
            'policy_desc':policy.policy_desc,
            'industry':policy.industry,
            'geography':",".join([data.geography for data in policy.geographies]),
            'log_level':policy.log_level,
            'code_checker': policy.code_checker,      
            'anonymize': policy.anonymize,  
            'block_pii':policy.block_pii,
            'policy_type':policy.policy_type,
            'injectionthreshold':getDescription(float(policy.injectionthreshold),'Injection'),
            'hatefulsentimentthreshold':getDescription(float(policy.hatefulsentimentthreshold),'Negativity'),
            'toxicitythreshold':getDescription(float(policy.toxicitythreshold),'Toxicity'),
            'entities':[data.entity.entity_value for data in policy.entities if data.entity],
            'topics':[data.topic.topic_name for data in policy.topics if data.topic],
            'regexs':[data.regex.regex_name for data in policy.regexs if data.regex],
            'metaprompts':[data.metaprompt.metaprompt_name for data in policy.metaprompts if data.metaprompt],
            'llms':[data.llm.llm_name for data in policy.llms if data.llm],
            'piientities':[data.piientity.pii_desc for data in policy.piientities if data.piientity],
            'phrases':[data.banned_phrase for data in policy.phrases],
            'prompts':prompts,
            'projects':[data.project.project_name for data in policy.projects if data.project],
            'modified_by': policy.modified_by,
            'modified_on': getFormattedDateTime(policy.modified_on),  # Convert datetime to string
            'created_on': getFormattedDateTime(policy.created_on),  # Convert datetime to string
            'created_by': policy.created_by
        } 
    return JSONResponse(content=serialized_policy, status_code=200)


@app.get("/getpolicy/{id}")
def GetPolicy(id:int, request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    policy = PolicyRepository.read(id)
    prompts=[]
    for prompt in policy.prompts:
        objprompt={
            'id':prompt.id,
            'prompt':prompt.prompt
        }
        prompts.append(objprompt)
    serialized_policy = {
            'id': policy.id,
            'name':policy.policy_name,
            'policy_desc':policy.policy_desc,
            'industry':policy.industry,
            'geography':[data.geography for data in policy.geographies],
            'log_level':policy.log_level,
            'code_checker': policy.code_checker,      
            'anonymize': policy.anonymize,  
            'block_pii':policy.block_pii,
            'policy_type':policy.policy_type,
            'injectionthreshold':float(policy.injectionthreshold),
            'hatefulsentimentthreshold':float(policy.hatefulsentimentthreshold),
            'toxicitythreshold':float(policy.toxicitythreshold),
            'entities':[data.entity_id for data in policy.entities],
            'topics':[data.topic_id for data in policy.topics],
            'regexs':[data.regex_id for data in policy.regexs],
            'llms':[data.llm_id for data in policy.llms],
            'piientities':[data.pii_name for data in policy.piientities],
            'phrases':[data.banned_phrase for data in policy.phrases],
            'metaprompts':[data.metaprompt_id for data in policy.metaprompts],
            'prompts':prompts,
            'modified_by': policy.modified_by,
            'modified_on': getFormattedDateTime(policy.modified_on),  # Convert datetime to string
            'created_on': getFormattedDateTime(policy.created_on),  # Convert datetime to string
            'created_by': policy.created_by
        }
    return JSONResponse(content=serialized_policy, status_code=200)

@app.post("/createpolicy")
def CreatePolicy(updatePolicyReq : UpdatePolicyModel, request : Request):
    username = isAuthenticated(request)
    if username is None:
         return UnauthenticatedUserResponseReturn() 
    # call repository
    # try:

    [result,id]=PolicyRepository.create(updatePolicyReq, username)
    if result==0:
        return JSONResponse(content={"message": "Policy created successfully.","id":id}, status_code=200)
    elif result==1:
        return JSONResponse(content={"message": "Policy doesnt exists."}, status_code=500)
    elif result==2:
        return JSONResponse(content={"message": "Duplicate policy name found."}, status_code=500)

@app.post("/updatepolicy/{id}")
async def UpdatePolicy(id : int, updatePolicyReq : UpdatePolicyModel, request : Request ):
    username = isAuthenticated(request)
    if username is None:
        return UnauthenticatedUserResponseReturn()

    # call repository
    try:
       
        result=PolicyRepository.update(updatePolicyReq, id, username)
        if result==0:
            await ClearProjectCache()
            return JSONResponse(content={"message": "Policy updated successfully."}, status_code=200)
        elif result==1:
            return JSONResponse(content={"message": "Policy doesnt exists."}, status_code=500)
        elif result==2:
            return JSONResponse(content={"message": "Duplicate Policy name found."}, status_code=500)
    except Exception as e:
        logger.error(f"Policy Update failed! {e}")
        return JSONResponse(content={"message": "Policy Update failed!"}, status_code=500)

@app.delete("/deletepolicy/{id}")
async def DeletePolicy(id : int, request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    # call repository
    try:
        result=PolicyRepository.delete(id)
        if result==0:
            await ClearProjectCache()
            return JSONResponse(content={"message": "Policy deleted successfully."}, status_code=200)
        elif result==1:
            return JSONResponse(content={"message": "Policy doesnt exist."}, status_code=500)
        elif result==2:
            return JSONResponse(content={"message": "Policy cannot be deleted as it is linked to application."}, status_code=500)
        elif result==3:
            return JSONResponse(content={"message": "Policy cannot be deleted as it is linked to App Group."}, status_code=500)
    except Exception as e:
        logger.error(f"Policy Deletion failed {e}")
        return JSONResponse(content={"message": "Policy deletion failed!"}, status_code=500)

def getDescription(score,key):
    filteredData=[]
    if key=="Negativity":
        filteredData= [data["desc"] for data in arrNegativity if data["score"]==score]
    else:
        filteredData= [data["desc"] for data in arrToxicity if data["score"]==score]
    if len(filteredData)>0:
        return filteredData[0]
    else :
        return ""

@app.get("/getpolicyprompts/{id}")
def GetPolicyPrompts(id:int,request : Request ):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
   
    prompts = PolicyRepository.getrelatedPrompts(id)
    serialized_prompts=[]
    for prompt in prompts:
        serialized_prompt = {
                'id': prompt.id,
                'prompt':prompt.prompt                
            } 
        serialized_prompts.append(serialized_prompt)
    return JSONResponse(content=serialized_prompts, status_code=200)


#endregion

#region PII Entity
@app.get("/getmasterdata")
def GetMasterData(request : Request):
    
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    
    piigroups = PIIRepository.readall()
    serialized_piigroups= []
    for piigroup in piigroups:
        serialized_piigroup = {
            'group_name': piigroup.group_name,
            'group_desc': piigroup.group_desc,
            'pii_entities':[]          
        }
        for piientity in piigroup.piientities:
            piiobj={
                'name':piientity.pii_name,
                'desc':piientity.pii_desc
            }
            serialized_piigroup['pii_entities'].append(piiobj)

        serialized_piigroups.append(serialized_piigroup)
        constants= readfileAndGetData("constants") 
        returnObj={
            "piientitygroups":serialized_piigroups,
            "policytypes":[constants["POLICY_TYPE"][key] for key in constants["POLICY_TYPE"].keys()],
            'loglevel':[constants["LOG_LEVEL"][key] for key in constants["LOG_LEVEL"].keys()],
            'industry':[constants["Industry"][key] for key in constants["Industry"].keys()],
            'geography':[constants["Geography"][key] for key in constants["Geography"].keys()],
        }
    return JSONResponse(content=returnObj, status_code=200) 

#endregion

#region AppGroups

@app.get("/getappgroups")
def GetAppGroups(request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
   
    appgrouplist =AppgroupRepository.readall()
    serialized_appgroups = []
    for appgroup in appgrouplist:
     
        serialized_appgroup = {
            'id': appgroup.id,
            'name':appgroup.group_name,  
            'desc'    :appgroup.group_desc,     
            'policies':[data.policy.policy_name for data in appgroup.policies if data.policy],           
            'modified_by': appgroup.modified_by,
            'modified_on': getFormattedDateTime(appgroup.modified_on),  # Convert datetime to string
            'created_on': getFormattedDateTime(appgroup.created_on),  # Convert datetime to string
            'created_by': appgroup.created_by
        }
        serialized_appgroups.append(serialized_appgroup)
    return JSONResponse(content=serialized_appgroups, status_code=200) 

@app.get("/getappgroup/{id}")
def Getappgroup(id :int, request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
   
    appgroup = AppgroupRepository.read(id)
    serialized_appgroup = {
            'id': appgroup.id,
            'name':appgroup.group_name, 
            'desc'    :appgroup.group_desc,             
            'policies':[data.policy_id for data in appgroup.policies],          
            'modified_by': appgroup.modified_by,
            'modified_on': getFormattedDateTime(appgroup.modified_on),  # Convert datetime to string
            'created_on': getFormattedDateTime(appgroup.created_on),  # Convert datetime to string
            'created_by': appgroup.created_by
        }
    return JSONResponse(content=serialized_appgroup, status_code=200) 

@app.post("/createappgroup")
def CreateAppgroup(appgroupReq : CreateAppgroupModel , request: Request):
    username = isAuthenticated(request)
    if username is None:
         return UnauthenticatedUserResponseReturn() 
    # call repository
    # try:
    result= AppgroupRepository.create(appgroupReq, username)
    if result==0:
        return JSONResponse(content={"message": "Appgroup created successfully."}, status_code=200) 
    elif result==1:
        return JSONResponse(content={"message":   "Appgroup doesnt exist."}, status_code=500) 
    elif result==2:
        return JSONResponse(content={"message":   "Duplicate Appgroup name exists."}, status_code=500) 
  
@app.post("/updateappgroup/{id}")
def UpdateAppgroup(id:int, appgroupReq : CreateAppgroupModel, request : Request ):
    username = isAuthenticated(request)
    if username is None:
        return UnauthenticatedUserResponseReturn()
    result=AppgroupRepository.update(appgroupReq,id, username)
    if result==0:
        return JSONResponse(content={"message":  "Appgroup updated successfully."}, status_code=200) 
    elif result==1:
        return JSONResponse(content={"message":   "Appgroup doesnt exist."}, status_code=500)
    elif result==2:
        return JSONResponse(content={"message":   "Duplicate Appgroup name exists."}, status_code=500)

@app.delete("/deleteappgroup/{id}")
def DeleteAppgroup(id : int , request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    # call repository
    try:       
      
        result= AppgroupRepository.delete(id)
        if result==0:    
            return JSONResponse(content={"message":   "Appgroup deleted successfully."}, status_code=200)       
        elif result==1:
            return JSONResponse(content={"message":   "Appgroup doesnt exist."}, status_code=500)
        elif result==2:
            return JSONResponse(content={"message":   "Appgroup cannot be deleted as it is linked to project."}, status_code=500)        
    except Exception as e:
        return JSONResponse(content={"message":   "Appgroup deletion failed!"}, status_code=500)

#endregion

#region Projects

@app.get("/getprojects")
def GetProjects(request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
   
    projectlist =ProjectRepository.readall()
    serialized_Projects = []
    for project in projectlist:
     
        serialized_project = {
            'id': project.id,
            'name':project.project_name, 
            'appgroup_id':  project.appgroup.group_name if   project.appgroup else "",   
            'project_desc':project.project_desc if not project.project_desc==None else "",
            'app_ci':project.app_ci if not project.app_ci==None else "",
            'app_url':project.app_url if not project.app_url==None else "",
            'owner_name':project.owner_name if not project.owner_name==None else "",
            'owner_handle':project.owner_handle if not project.owner_handle==None else "",
            'owner_email':project.owner_email if not project.owner_email==None else "",
            'approver_name':project.approver_name if not project.approver_name==None else "",
            'approver_handle':project.approver_handle if not project.approver_handle==None else "",
            'approver_email':project.approver_email if not project.approver_email==None else "",
            'from_date':getFormattedDateTimeWithoutTimeZone(project.from_date) if not project.from_date==None else "",
            'to_date':getFormattedDateTimeWithoutTimeZone(project.to_date) if not project.to_date==None else "",
            'locked':project.locked if not project.locked==None else "",
            'active':project.active if not project.active==None else "",
            'policies':[data.policy.policy_name for data in project.policies if data.policy],           
            'modified_by': project.modified_by,
            'modified_on': getFormattedDateTime(project.modified_on),  # Convert datetime to string
            'created_on': getFormattedDateTime(project.created_on),  # Convert datetime to string
            'created_by': project.created_by
        }
        serialized_Projects.append(serialized_project)
    return JSONResponse(content=serialized_Projects, status_code=200)

@app.get("/getproject/{id}")
def Getproject(id : int, request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
   
    project = ProjectRepository.read(id)
    serialized_project = {
            'id': project.id,
            'name':project.project_name,  
            'appgroup_id':  project.appgroup_id if not project.appgroup_id==None else "", 
            'project_desc':project.project_desc if not project.project_desc==None else "", 
            'app_ci':project.app_ci if not project.app_ci==None else "",
            'app_url':project.app_url if not project.app_url==None else "",
            'owner_name':project.owner_name if not project.owner_name==None else "",
            'owner_handle':project.owner_handle if not project.owner_handle==None else "",
            'owner_email':project.owner_email if not project.owner_email==None else "",
            'approver_name':project.approver_name if not project.approver_name==None else "",
            'approver_handle':project.approver_handle if not project.approver_handle==None else "",
            'approver_email':project.approver_email if not project.approver_email==None else "",
            'from_date':getFormattedDateTimeWithoutTimeZone(project.from_date) if not project.from_date==None else "",
            'to_date':getFormattedDateTimeWithoutTimeZone(project.to_date) if not project.to_date==None else "",
            'locked':project.locked if not project.locked==None else "",
            'active':project.active if not project.active==None else "",          
            'policies':[data.policy_id for data in project.policies],          
            'modified_by': project.modified_by,
            'modified_on': getFormattedDateTime(project.modified_on),  # Convert datetime to string
            'created_on': getFormattedDateTime(project.created_on),  # Convert datetime to string
            'created_by': project.created_by
        }
    return JSONResponse(content=serialized_project, status_code=200)

@app.post("/createproject")
def CreateProject(projReq : CreateProjectModel, request : Request):
    username = isAuthenticated(request)
    if username is None:
         return UnauthenticatedUserResponseReturn() 
    # call repository
    # try:
    result= ProjectRepository.create(projReq, username)
    if result==0:
        return JSONResponse(content={"message": "Application created successfully."}, status_code=200)
    elif result==1:
        return JSONResponse(content={"message": "Application doesnt exist."}, status_code=500)
    elif result==2:
        return JSONResponse(content={"message": "Duplicate Application name exists."}, status_code=500)

@app.post("/updateproject/{id}")
async def UpdateProject(id : int, projReq : CreateProjectModel, request : Request):
    username = isAuthenticated(request)
    if username is None:
        return UnauthenticatedUserResponseReturn()

    result=ProjectRepository.update(projReq,id, username)
    if result==0:
        await ClearProjectCache()
        return JSONResponse(content={"message": "Application updated successfully."}, status_code=200)
    elif result==1:
        return JSONResponse(content={"message": "Application doesnt exist."}, status_code=500)
    elif result==2:
        return JSONResponse(content={"message": "Duplicate Application name exists."}, status_code=500)

@app.delete("/deleteproject/{id}")
async def DeleteProject(id : int, request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    # call repository
    try:
        ProjectRepository.delete(id)
        await ClearProjectCache()
        return JSONResponse(content={"message": "Application deleted successfully."}, status_code=200)
    except Exception as e:
        logger.error(f"an error occurred: {e}")
        return JSONResponse(content={"message": "Application deletion failed!"}, status_code=500)

@app.get("/getprojectview/{id}")
def GetprojectView(id : int , request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
   
    constants= readfileAndGetData("constants") 
    startime=time.time()  
    project = ProjectPolicyDetailsRepository.GetProjectView(id,constants)
    project['injectionthreshold']=getDescription(float(project['injectionthreshold']),'Injection')
    project['hatefulsentimentthreshold']=getDescription(float(project['hatefulsentimentthreshold']),'Negativity')
    project['toxicitythreshold']=getDescription(float(project['toxicitythreshold']),'Toxicity')
    return JSONResponse(content=project, status_code=200)

@app.post("/publish/{id}")
async def PublishProject(id : int , request : Request):
    username = isAuthenticated(request)
    if username is None:
         return UnauthenticatedUserResponseReturn() 
    # call repository
  
    result= ProjectPolicyDetailsRepository.PublishProject(id, username)
    if result==0:
        await ClearProjectCache()
        return JSONResponse(content={"message": "Application published successfully."}, status_code=200)
    elif result==1:
        return JSONResponse(content={"message": "Inactive or Locked Application cannot be published."}, status_code=500)
    elif result==2:
        return JSONResponse(content={"message": "Published version of Application is Inactive or Locked."}, status_code=500)

@app.get("/getturingprompts/{id}")
def GetTuringPrompts(id:int , request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()      
    [prompts,llms] = ProjectRepository.getprojectpromptsandllms(id)
    return JSONResponse(content={'prompts':prompts,'llms':llms}, status_code=200)

@app.get("/getprojectversions/{id}")
def GetVersionForTuringPrompt(id : str, request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()  
        
    versions =VersionRepository.getAllVersions(id)
    serialized_versions = []
    serialized_versions.append({
         'id': 'pre-prod',
          'number':"Pre-Publish"
    })   
    for version in versions:
     
        serialized_version = {
            'id': "latest" if version.is_latest=="Y" else version.id,
            'number':version.version_no
            
        }
        serialized_versions.append(serialized_version)
    return JSONResponse(content=serialized_versions, status_code=200)

@app.post("/runturingprompt/{project_id}/{versionid}")
async def RunTuringPrompt(project_id : int, versionid : str, promptReq : RunTuringPromptModel, request : Request):  
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()  
 
    if promptReq.prompt:  
        if promptReq.llm:           
            logger.info(f"Starting Guardrail: Violation Check")  
            logger.info(f"Initiating Project Get")
            progetstart=time.time()   
            projectDetails=await ProjectPolicyDetailsRepository.ValidateLicense(project_id,"",versionid)
            logger.info(f"View Get Time {time.time()- progetstart}")
            validlicensetime=time.time()
            if projectDetails:
                context=GuardrailContexModel(llm=promptReq.llm,
                                             username="",
                                             hostname="",
                                             ip="",
                                             israg="N",
                                             isChat="N")
                constants= readfileAndGetData("constants")  
                resultObj=RunGuardRail(projectDetails,context,promptReq.prompt,"",constants["INVOCATION_TYPE"]["REQ"],logging=False)
                if not resultObj["NoMatch"]:                 
                    return JSONResponse(content={"finalResult":resultObj["finalResult"],"FailureReasons": resultObj["FailureReasons"],"reasonForResult":resultObj["reasonForResult"]}, status_code=200)
                else:
                    logger.error(f"No Policy Matching specified LLM Found Application:{project_id} and llm:{promptReq.llm}.")
                    return JSONResponse(content={"message":   "No Policy Matching specified LLM Found."}, status_code=500)
            else:
                logger.error(f"Application:{project_id} with version {versionid} not found.")
                return JSONResponse(content={"message":   f"Application:{project_id} with version {versionid} not found."}, status_code=500)           
        else:
            logger.error(f"LLM Info missing")
            return JSONResponse(content={"message": "LLM Info missing."}, status_code=500)  
    else:
        logger.error(f"No Prompt found.")
        return JSONResponse(content={"message":   "No prompt specified."}, status_code=500)
   
@app.get("/runturingbot/{project_id}/{versionid}/{llm}/{token}")
async def RunTuringPrompts(project_id : int,versionid : str,llm : str,token : str):
    if not AutheticateTuringPrompt(project_id,versionid,llm,token):
        return UnauthenticatedUserResponseReturn()  
    logger.info(f"Getting Prompts")  
    prompts = ProjectRepository.getprojectprompts(project_id)
    promptlist=[data['prompt'] for data in prompts]
    logger.info(f"Starting Guardrail: Violation Check")  
    logger.info(f"Initiating Project Get")
    progetstart=time.time()   
    projectDetails=await ProjectPolicyDetailsRepository.ValidateLicense(str(project_id),"",versionid)
    logger.info(f"View Get Time {time.time()- progetstart}")
    if projectDetails:
        context=GuardrailContexModel(llm=llm,
                                             username="",
                                             hostname="",
                                             ip="",
                                             israg="N",
                                             isChat="N")
        constants= readfileAndGetData("constants")  
    async def streamresponse(promptlist,projectDetails,context,llm):
        try:
            index=-1
            while index<len(promptlist)-1:
                index+=1                   
                resultObj=RunGuardRail(projectDetails,context,promptlist[index],"",constants["INVOCATION_TYPE"]["REQ"],logging=False)
                if not resultObj["NoMatch"]:                 
                    yield 'data: {}\n\n'.format(json.dumps({
                    "finalResult":resultObj["finalResult"],
                    "FailureReasons": resultObj["FailureReasons"],
                    "prompt":promptlist[index],
                    "reasonForResult":resultObj["reasonForResult"]
                }))
                
                else:
                    logger.error(f"No Policy Matching specified LLM Found Application:{project_id} and llm:{llm}")
                    yield 'data: {}\n\n'.format(json.dumps({
                    'error':"No Policy Matching specified LLM Found"
                    })) 
            yield 'data: {}\n\n'.format(json.dumps({
                    'close':"Y"
                    }))    
        except Exception as e:
            logger.exception(f"An application Error Occured {e}")
            yield 'data: {}\n\n'.format(json.dumps({
                    'message': "Turing prompt failed to process!"
                    })) 
            return          
    return StreamingResponse(streamresponse(promptlist,projectDetails,context,llm), media_type="text/event-stream", headers={'X-Accel-Buffering': 'no','Connection': 'keep-alive', 'Cache-Control':'no-cache'})
      
@app.get("/gettemptoken/{project_id}/{versionid}/{llm}")
def createTuringTemptoken(project_id : int, versionid : str, llm : str, request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()  
    secret=getKeyVaultSecret(config_data["JWT-KEY"])
    payload_data = {
                "project_id": project_id   ,
                "versionid":versionid,
                "llm":llm,
                "username":username,
                "exp": getCurrentDateTime() + datetime.timedelta(seconds=30)          
               }
    token=  jwt.encode(
                payload=payload_data,
                key=secret,
                algorithm="HS256"
                )
    return JSONResponse(content={'token':token}, status_code=200)
  
    
    


#endregion

#region PublishedProject

@app.get("/getversions/{id}")
def GetProjectVersions(id: str, request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
   
    versions =VersionRepository.getinactiveVersions(id)
    serialized_versions = []
    for version in versions:
     
        serialized_version = {
            'id': version.id,
            'number':version.version_no
            
        }
        serialized_versions.append(serialized_version)
    return JSONResponse(content=serialized_versions, status_code=200)

@app.post("/rollback/{projid}/{versionid}")
async def RollbackProject(projid : str, versionid : str, request: Request ):
    username = isAuthenticated(request)
    if username is None:
         return UnauthenticatedUserResponseReturn() 
    # call repository
  
    result= VersionRepository.rollbackversion(projid,versionid, username)
    if result==0:
        await ClearProjectCache()
        return JSONResponse(content={"message": "Application RolledBack successfully."}, status_code=200)
    elif result==2:
        return JSONResponse(content={"message": "Published version of Application is Inactive or Locked."}, status_code=500)

@app.get("/getpublishedprojects")
def GetPublishedProjects(request: Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
   
    [projects,activeVersions] =VersionRepository.getallpublishedProjects()
    serialized_projects = []
    for project in projects:
        versiumNum=""
        versiumNum=[data.version_no for data in activeVersions if data.project_id==project[0]]
        if (len(versiumNum)==1):
            versiumNum=versiumNum[0]       
        serialized_project = {
            'id': project[0],
            'name':project[1],
            'project_desc':project[2],
            'created_on':getFormattedDateTime(project[3]),
            'active':project[4],
            'locked':project[5],
            'created_by':project[6],
            'modified_by':project[7],
            'modified_on':getFormattedDateTime(project[8]),
            'version_num':versiumNum
        }
        serialized_projects.append(serialized_project)
    return JSONResponse(content=serialized_projects, status_code=200)

@app.get("/getpublishedprojectview/{id}/{versionid}")
def GetPublishedprojectView(id:str ,versionid : str, request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
   
    constants= readfileAndGetData("constants") 
    startime=time.time()  
    project = ProjectPolicyDetailsRepository.GetPublishedProjectDetails(id,constants,versionid)
    project['injectionthreshold']=getDescription(float(project['injectionthreshold']),'Injection')
    project['hatefulsentimentthreshold']=getDescription(float(project['hatefulsentimentthreshold']),'Negativity')
    project['toxicitythreshold']=getDescription(float(project['toxicitythreshold']),'Toxicity')
    return JSONResponse(content=project, status_code=200)

@app.post("/deactivatepublished/{projid}")
async def DeactivatePublished(projid: str, request : Request):
    username = isAuthenticated(request)
    if username is None:
         return UnauthenticatedUserResponseReturn() 
    # call repository
  
    result= VersionRepository.activedeactive(projid,"N", username)
    await ClearProjectCache()
    return JSONResponse(content={"message": "Application Deactivated successfully."}, status_code=200)

@app.post("/activatepublished/{projid}")
async def ActivatePublished(projid:str, request : Request):
    username = isAuthenticated(request)
    if username is None:
         return UnauthenticatedUserResponseReturn() 
    # call repository
  
    result= VersionRepository.activedeactive(projid,"Y", username)
    await ClearProjectCache()
    return JSONResponse(content={"message": "Application Activated successfully."}, status_code=200)

@app.post("/lockpublished/{projid}")
async def LockPublished(projid : str, request : Request ):
    username = isAuthenticated(request)
    if username is None:
         return UnauthenticatedUserResponseReturn() 
    # call repository
  
    result= VersionRepository.lockedunlock(projid,"Y", username)
    await ClearProjectCache()
    return JSONResponse(content={"message": "Application Locked successfully."}, status_code=200)

@app.post("/unlockpublished/{projid}")
async def UnLockPublished(projid : str , request : Request):
    username = isAuthenticated(request)
    if username is None:
         return UnauthenticatedUserResponseReturn() 
    # call repository
  
    result= VersionRepository.lockedunlock(projid,"N", username)
    await ClearProjectCache()
    return JSONResponse(content={"message": "Application Unlocked successfully."}, status_code=200)

@app.get("/getprojectconfig/{id}")
def GetprojectConfig(id : str , request : Request):
    try:
        username = isAuthenticated(request)
        if username is None:
            return UnauthenticatedUserResponseReturn()
    
        project = VersionRepository.getProjectForConfig(id)
        urlobj= parse.urlsplit(str(request.url))
        basepath=config_data["BASE_PATH"]  
        url=f"{urlobj.scheme}://{urlobj.netloc}{basepath}/guardrail"
        anonymizeurl=f"{urlobj.scheme}://{urlobj.netloc}{basepath}/anonymize"
        deanonymizeurl=f"{urlobj.scheme}://{urlobj.netloc}{basepath}/deanonymize"
        project={
            'name':project[0],  
            'key':project[1],
            'url':url,
            'anonymizeurl':anonymizeurl,
            'deanonymizeurl':deanonymizeurl
        }   
        return StreamingResponse( GenerateConfigFile(project), media_type="application/octet-stream")
    except Exception as e:
        logger.error(f"An Application Error occured: {e}")
        return JSONResponse(content={"message": "Failed to get project configuration."}, status_code=500)

@app.get("/export/{id}")
def ExportProject(id : str ,request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
   
    result = VersionRepository.exportprojectdata(id)   
    projects=[]
    topics=[] 
    for project in result[0]:
        objproject={
                'project_id':project.project_id,
                'policy_id' :project.policy_id,
                'llm_name' :project.llm_name,
                'log_level':project.log_level,
                'code_checker':project.code_checker,
                'anonymize':project.anonymize,
                'block_pii':project.block_pii,
                'policy_type':project.policy_type,
                'topic_name':project.topic_name,
                'regex_name' :project.regex_name,
                'regex_value' :project.regex_value,
                'metaprompt_id' :project.metaprompt_id,
                'metaprompt_value' :project.metaprompt_value,
                'entity_value' :project.entity_value,
                'license_key':project.license_key,
                'watermark_text':project.watermark_text,
                'pii_name' :project.pii_name,
                'pii_desc' :project.pii_desc,
                'banned_phrase':project.banned_phrase,
                'project_name' :project.project_name,
                'policy_name' :project.policy_name,
                'metaprompt_name' :project.metaprompt_name,
                'injectionthreshold':float(project.injectionthreshold),
                'hatefulsentimentthreshold':float(project.hatefulsentimentthreshold),
                'toxicitythreshold':float(project.toxicitythreshold),
                'project_desc' :project.project_desc,
                'app_ci':project.app_ci,
                'app_url':project.app_url,
                'owner_name':project.owner_name,
                'owner_handle':project.owner_handle,
                'owner_email':project.owner_email,
                'approver_name':project.approver_name,
                'approver_handle':project.approver_handle,
                'approver_email':project.approver_email,
                'from_date':getFormattedDateTimeWithoutTimeZone(project.from_date),
                'to_date':getFormattedDateTimeWithoutTimeZone(project.to_date),
                'locked':project.locked,
                'active':project.active,
                'modified_by' :project.modified_by,
                'modified_on' :getFormattedDateTime(project.modified_on),
                'created_on' :getFormattedDateTime(project.created_on),
                'created_by':project.created_by
        }
        projects.append(objproject)
    for topic in result[1]:
        objtopic={
            'project_id':topic.project_id,
            'topic_name' :topic.topic_name ,   
            'created_on' :getFormattedDateTimeWithoutTimeZone(topic.created_on)
        }
        topics.append(objtopic)
    exportdata={
         'projects':projects,  
         'topics':topics ,
         'env':config_data["ENV"]     
    }   
    return StreamingResponse( GenerateExportFile(exportdata), media_type="application/octet-stream")

@app.post("/import")
async def ImportProject(file: UploadFile, request : Request):
     username = isAuthenticated(request)
     if username is None:
       return UnauthenticatedUserResponseReturn()
     if not file:
        return JSONResponse(content={'message':'File not found.'}, status_code=500)
     else:
        filetype = os.path.splitext(file.filename)[-1]
        if not filetype == ".data":
            logger.info(f"File type not supported")
            return JSONResponse(content={"message":"File type not supported."}, status_code=500)

        file = file.file
        size =  request.headers.get("Content-Length")
        if int(size) > config_data["PROJECT_FILE_SIZE"]:
            logger.info(f"File size exceeded while uploading project.")
            return JSONResponse(content={"message":"File size exceeded."}, status_code=500)
        
        result=GetImportedFileData(file)
        if result[0]==0:
            [projects,topics,env]=result[1]            
            if not env==config_data["ENV"]:
                for project in projects:
                    project["project_id"]=f"{env}-{project['project_id']}"
                for topic in topics:
                    topic["project_id"]=f"{env}-{topic['project_id']}"
            project_id=projects[0]['project_id']
            result=VersionRepository.ImportProject(project_id,projects,topics,username)
            if result==0:
                await ClearProjectCache()
                return JSONResponse(content={"message": "Application Imported Successfully."}, status_code=200)
            elif result==2:
                return JSONResponse(content={"message": "Published version of Application is Inactive or Locked."}, status_code=500)
        elif result[0]==1:
            return JSONResponse(content={"message":   "Imported file not in proper format."}, status_code=500)
       
@app.get("/getpublishedprojectpolicies")
def GetPublishedProjectPolicies(request : Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
   
    [projects,policies] =VersionRepository.GetProjectPolicyForDashboard()
    result={
        'projects':projects,
        'policies':policies
    }       
    return JSONResponse(content=result, status_code=200)

@app.delete("/deletepublishedproject/{id}")
async def DeletePublishedProject(id : str,request : Request ):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    # call repository
    try:
        VersionRepository.deletepublishedapp(id)
        await ClearProjectCache()
        return JSONResponse(content={"message": "Published Application deleted successfully."}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": "Published Application deletion failed!"}, status_code=500)


#endregion

#region Users

@app.get("/getusers")
def GetUsers(request : Request):
    
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    
    users = UserRepository.readall()
    serialized_users = []
    for user in users:
        serialized_user = {
            'id': user.id,
            'username': user.username,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'user_role':user.user_role,
            'active': user.active,
            'locked': user.locked,
            'lockeddatetime':getFormattedDateTime(user.lockeddatetime) if not user.lockeddatetime==None else "",
            'lastlogintime':getFormattedDateTime(user.lastlogintime) if not user.lastlogintime==None else "",
            'modified_by': user.modified_by,
            'modified_on': getFormattedDateTime(user.modified_on),  # Convert datetime to string
            'created_on': getFormattedDateTime(user.created_on),  # Convert datetime to string
            'created_by': user.created_by
        }
        serialized_users.append(serialized_user)
    return JSONResponse(content=serialized_users, status_code=200) 

@app.post("/updateuser/{id}")
def UpdateUser(id:int, updateUserReq : UpdateUserModel, request :Request ):
    username = isAuthenticated(request)
    if username is None:
        return UnauthenticatedUserResponseReturn()

    # call repository
    try:
        
        result=UserRepository.update(updateUserReq,id, username)
        if result==0:   
            return JSONResponse(content={"message":  "User updated successfully."}, status_code=200)        
        elif result==1:
            return JSONResponse(content={"message":   "User doesnt exist."}, status_code=500)
        elif result==2:
            return JSONResponse(content={"message":   "Duplicate Username exists."}, status_code=500)
    except Exception as e:
        logger.error(f"User Update failed {e}")
        return JSONResponse(content={"message":   "User Update failed!"}, status_code=500)

@app.post("/createuser")
def CreateUser(createUserReq : CreateUserModel, request : Request):
    username = isAuthenticated(request)
    if username is None:
        return UnauthenticatedUserResponseReturn()

    # call repository
    try:
        defaultpwd=getKeyVaultSecret(config_data["DEFAULT_KEY"])
        
        
        hashedPass = encryptPass(defaultpwd)
        
        result=UserRepository.create(createUserReq, username, hashedPass)
        if result==0:      
            return JSONResponse(content={"message":  "User created successfully."}, status_code=200)     
        elif result==1:
            return JSONResponse(content={"message":   "User doesnt exist."}, status_code=500)
        elif result==2:
            return JSONResponse(content={"message":   "Duplicate Username exists."}, status_code=500)
    except Exception as e:
        logger.error(f"User Creation failed {e}")
        return JSONResponse(content={"message":   "User Creation failed!"}, status_code=500)

@app.post("/deactivateuser/{id}")
def DeactivateUser(id:int,request:Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    # call repository
    try:
        
        result= UserRepository.deactivate(id,username)
        if result==0:
            return JSONResponse(content={"message":   "User deactivated successfully."}, status_code=200)
        elif result==1:
            return JSONResponse(content={"message":   "User doesnt exist."}, status_code=500)       
    except Exception as e:
        logger.error(f"User Deactivation failed {e}")
        return JSONResponse(content={"message":   "User Deactivation failed!"}, status_code=500)

@app.post("/activateuser/{id}")
def ActivateUser(id:int,request:Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    # call repository
    try:
        
        result= UserRepository.activate(id,username)
        if result==0:
            return JSONResponse(content={"message":   "User activated successfully."}, status_code=200)
        elif result==1:
            return JSONResponse(content={"message":   "User doesnt exist."}, status_code=500)       
    except Exception as e:
        logger.error(f"User activation failed {e}")
        return JSONResponse(content={"message":   "User activation failed!"}, status_code=500)

@app.post("/unlockuser/{id}")
def UnlockUser(id:int,request:Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    # call repository
    try:
        
        result= UserRepository.unlock(id,username)
        if result==0:
            return JSONResponse(content={"message":   "User unlocked successfully."}, status_code=200)
        elif result==1:
            return JSONResponse(content={"message":   "User doesnt exist."}, status_code=500)       
    except Exception as e:
        logger.error(f"User unlock failed {e}")
        return JSONResponse(content={"message":   "User unlock failed!"}, status_code=500)       

@app.post("/changepwd")
def changepwd(changePassReq : ChangePasswordModel, request:Request):
     username = isAuthenticated(request)
     if username is None:
        return UnauthenticatedUserResponseReturn()

     pwd=changePassReq.oldpassword
     newpwd=changePassReq.newpassword
     result=UserRepository.changepwd(username,pwd,newpwd,config_data["INCORRECT_PWD_COUNT"])
     if result==0: 
        return JSONResponse(content={"message":"Success"}, status_code=200)       
     elif result==1:
        return JSONResponse(content={"message":"Incorrect UserId/Password Specified."}, status_code=500)       
     elif result==2:
        return JSONResponse(content={"message":"User account is locked. Please contact the administrator."}, status_code=500)  
     elif result==3:
        return JSONResponse(content={"message":"User account is deactivated. Please contact the administrator."}, status_code=500)  

@app.get("/getusermasterdata")
def GetUserMasterData(request:Request):
    
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()    
   
    constants= readfileAndGetData("constants") 
    returnObj={       
        "user_roles":[constants["USER_ROLES"][key] for key in constants["USER_ROLES"].keys()]       
    }
    return JSONResponse(content=returnObj, status_code=200)  

@app.post("/getuserfromhandle")
def GetUserNameFromHandle(userHandelReq : GetUserFromHandelModel, request:Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    # call repository
    try:
        appusername=userHandelReq.username
        result=ReturnUserName(appusername,config_data["PSEUDO-KEY"])
        UserRepository.loguserhandelsearch(appusername,username)
        return JSONResponse(content={"username": result}, status_code=200)
    except Exception as e:
        logger.error(f"User deanonymization failed {e}")
        return JSONResponse(content={"message":   "User deanonymization failed!"}, status_code=500)



@app.post("/saveusersetting")
def GetUserNameFromHandle(usersettingReq : UserSettingModel, request:Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    # call repository
    try:
  
        result=UserRepository.saveSettings(username,usersettingReq)
        if result==0:
            return JSONResponse(content={"success": True}, status_code=200)
        elif result==1:
            return JSONResponse(content={"message":   "User not found!"}, status_code=500)
    except Exception as e:
        logger.error(f"Error in Saving User Setting failed {e}")
        return JSONResponse(content={"message":   "User setting change failed!"}, status_code=500)


#endregion
    
# region Authentication
def createJWTToken(username,role):
    secret=getKeyVaultSecret(config_data["JWT-KEY"])
    payload_data = {
                "username": username,
                "role" :role,
                "exp": getCurrentDateTime() + datetime.timedelta(seconds=config_data["SESSION_TIMEOUT"])          
               }
    return jwt.encode(
                payload=payload_data,
                key=secret,
                algorithm="HS256"
                )#.decode('utf-8')    

@app.post("/authenticate")
def Authenticate(authentication : AuthenticationModel):  
     username=authentication.username
     pwd=authentication.password
     (result,user)=UserRepository.authenticate(username,pwd,config_data["INCORRECT_PWD_COUNT"])
     if result==0:   
        full_name=user.firstname + " " +  user.lastname
        setupuri=""
        usertoken=""
        if user.is_two_factor_required=="Y" and user.is_two_factor_enabled=="N":
            setupuri=OTPManager.get_setup_uri(username,user.secret_token)
            usertoken=user.secret_token
        
        responseObj={
            "message":"Success",
            "name":full_name,
            "env":config_data["ENV"],
            "2fa_required":user.is_two_factor_required,
            "2fa_enabled":user.is_two_factor_enabled,
            "setupuri":setupuri,
            "token":usertoken}
        if user.is_two_factor_required=="N":
            logger.info(f"username {username} user.user_role {user.user_role}")
            token= createJWTToken(username,user.user_role)            
            header={"x-access-token":token,"Access-Control-Expose-Headers":"x-access-token"}
            return JSONResponse(content=responseObj, status_code=200, headers=header)
        else:
            return JSONResponse(content=responseObj, status_code=200 )
     elif result==1:
        return JSONResponse(content={"message":"Incorrect UserId/Password Specified."}, status_code=401 )
     elif result==2:
        return JSONResponse(content={"message":"User account is locked. Please contact the administrator."}, status_code=401 )
     elif result==3:
        return JSONResponse(content={"message":"User account is deactivated. Please contact the administrator."}, status_code=401  )

@app.post("/verifyotp")
def VerifyOTP(otpReq : VerifyOTPModel): 
     username=otpReq.username
     code=otpReq.code
     user=UserRepository.getuserfromusername(username)
     result=OTPManager.validate_otp(code,username,user.secret_token)
     if result:
         UserRepository.recordLastLogin(username)
         full_name=user.firstname + " " +  user.lastname
         responseObj={
            "message":"Success",
            "name":full_name,
            "env":config_data["ENV"]
            }
         token= createJWTToken(otpReq.username,user.user_role)            
         header={"x-access-token":token,"Access-Control-Expose-Headers":"x-access-token"}
         return JSONResponse(content=responseObj,headers=header, status_code=200 )
     else:
        return JSONResponse(content={"message":"Incorrect OTP Entered."}, status_code=401)
  
@app.get("/getpermissions")
def GetUserPermissions(request: Request):
     username = isAuthenticated(request)
     if username is None:
       return UnauthenticatedUserResponseReturn()
     user=UserRepository.getuserfromusername(username)    
     if user:       
         role=user.user_role
         permissions=RoleMapping[role]
         pwd_change_req = user.required_pwd_change   
         settings=[]
         for setting in user.settings:
             settings.append({                 
                 'setting_name':setting.setting_name,
                 'setting_value':setting.setting_value
             })     
         responseObj={
            "message":"Success",          
            "role":role,
            "permissions":permissions,
            'required_pwd_change': pwd_change_req,
            "settings":settings
            }
         return JSONResponse(content=responseObj, status_code=200 )
     else:
        return JSONResponse(content={"message":"Incorrect Username."}, status_code=401 )

@app.post("/validateusername")
def ValidateUsername(usernameReq : ValidateUsernameModel):
    if usernameReq:
        if usernameReq.username:
            username=(usernameReq.username).strip()
            user = UserRepository.getuserfromusername(username)
            if user:
                if user.active == "Y" and user.locked == "N":
                    if user.is_two_factor_enabled == "Y":
                        return JSONResponse(content={"message":"success"})
                    else:
                        return JSONResponse(content={"message": "User don't have two factor enabled."}, status_code=500)
                else:
                    return JSONResponse(content={"message": "User account is deactivated or locked. Please contact the administrator."}, status_code=500)
            else:
                return JSONResponse(content={"message": "User doesn't exist."}, status_code=500)
 
@app.post("/resetpassword")
def ResetPassword(resetpassReq : ResetPasswordModel):
    try:
        username=(resetpassReq.username).strip()
        code = (resetpassReq.code)
        password = resetpassReq.password
        user = UserRepository.getuserfromusername(username)
        if user:
            if user.active == "Y" and user.locked == "N":
                if user.is_two_factor_enabled == "Y":
                    result = OTPManager.validate_otp(code,username,user.secret_token)
                    if result:
                        result=UserRepository.resetpwd(username,password)
                        if result == 0:
                            return JSONResponse(content={"message":"Success"}, status_code=200)  
                    else:
                        return JSONResponse(content={"message":"Incorrect OTP Entered."}, status_code=401)    
                else:
                    return JSONResponse(content={"message": "User don't have two factor enabled."}, status_code=500)
            else:
                return JSONResponse(content={"message": "User account is deactivated or locked. Please contact the administrator."}, status_code=500)
        else:
            return JSONResponse(content={"message": "User doesn't exist."}, status_code=500)
    except Exception as e:
        logger.error(f"An application error occured while password reset {e}")
        return JSONResponse(content={"message": "Something went wrong. Can't complete the request."}, status_code=500)
    
         

def UnauthenticatedUserResponseReturn():
    return JSONResponse(content={"message": "user is unauthenticated."}, status_code=401)
#endregion

#region request interceptor
@app.middleware("http")
async def request_processor(request: Request, call_next):
    try:
        #add log and rbac 
        username,role = getuserrole(request)
        client_host = request.client.host
        urlobj= parse.urlsplit(str(request.url))
        logger.info(f'User - {username} from source {client_host} accessing {urlobj.path}')        
        if role:
            allowed=checkRoleAccess(urlobj,role)
            logger.info(f"Role Access: {urlobj} {role}. Result :{allowed}")
            if not allowed:
                return JSONResponse(content={"message":"The request can't be processed due to insufficient permissions."}, status_code=401)
        
        response = await call_next(request)
        
        logger.info(f'User - {username} with {role} role, from source {client_host} accessing {request.url} response status_code {response.status_code}')
        if response.status_code==200:
            if username:
                token=createJWTToken(username,role)
                response.headers['x-access-token'] = token
                response.headers['X-Accel-Buffering']="no"
                
                response.headers['Access-Control-Expose-Headers'] = "x-access-token,X-Accel-Buffering"
        elif response.status_code==422:
            response.status_code=500      
        
        response.headers['Cache-Control']="no-store, no-cache, must-revalidate"     
        response.headers["X-Frame-Options"] = 'SAMEORIGIN'
        response.headers["X-Content-Type-Options"] = 'nosniff'  
        return response
    except Exception as ex:
        logger.error(f"An Application Error occured: {ex}")
        return JSONResponse(content={"message":"An error occured in processing the request."}, status_code=500)

def checkRoleAccess(urlobj,role):
    path=str(urlobj.path).replace("/","")
    matchedKey=[data for data in RoleAccess.keys() if data==path]
    if len(matchedKey)>0:
        access_key=RoleAccess[matchedKey[0]]
        if access_key in RoleMapping[role]:
            return True
        else :
            return False
    else:
        return True
#endregion

#region GuardRailInvocation
     
@app.post("/guardrail")
async def GuardRail(grReq : GuardrailModel):  
    if grReq.projconfig and grReq.projconfig.key and grReq.projconfig.name: 
       project_id=grReq.projconfig.name
       license_key=grReq.projconfig.key
       context=grReq.context if grReq.context else ""
       if grReq.prompt:  
            if grReq.context and grReq.context.username and grReq.context.llm:     
              if grReq.invocation_id and grReq.invocation_type: 
                statrtime=time.time()           
                logger.info(f"Starting Guardrail: Violation Check")
                grReq.context.username=GeneratePseudoUserName(grReq.context.username,config_data["PSEUDO-KEY"])
                violationcount=PolicyViolationRepository.CheckPerUserViolation(grReq.context.username,project_id)
                logger.info(f"{violationcount} violations found in {time.time()-statrtime}")
                if violationcount>config_data["THRESHOLD_VIOLATION_COUNT"]:
                    return JSONResponse(content={"AllowPrompt":False, "updatedPrompt":"You are blocked from accessing the LLMs due to too many Guardrail violations."}, status_code=200)
                logger.info(f"Initiating Project Get")
                progetstart=time.time()   
                projectDetails= await ProjectPolicyDetailsRepository.ValidateLicense(project_id,license_key)
                logger.info(f"View Get Time {time.time()- progetstart}")
                validlicensetime=time.time()
                if projectDetails:
                    currentDate=getCurrentDateTime()
                    todate=projectDetails.to_date + datetime.timedelta(days=1)
                    if projectDetails.active=="N":
                        logger.error(f"Application :{project_id} is Inactive")
                        return JSONResponse(content={"message": "Application is Inactive."}, status_code=500)
                    elif projectDetails.locked=="Y":
                        logger.error(f"Application :{project_id} is Locked")
                        return JSONResponse(content={"message": "Application is Locked."}, status_code=500)
                    elif currentDate<projectDetails.from_date or currentDate>todate:
                        logger.error(f"Application :{project_id} is outside valid duration")
                        return JSONResponse(content={"message": "Application is outside valid duration."}, status_code=500)
                    else:
                        resultObj=RunGuardRail(projectDetails,grReq.context,grReq.prompt,grReq.invocation_id,grReq.invocation_type,appkey=config_data["ANON-KEY"])
                        if not resultObj["NoMatch"]:
                            return JSONResponse(content=resultObj, status_code=200)
                        else:
                            logger.error(f"No Policy Matching specified LLM Found Application:{project_id} and License:{license_key} and context:{context}")
                            return JSONResponse(content={"message": "No Policy Matching specified LLM Found."}, status_code=500)
                else:
                    logger.error(f"Project and License Key doesnt match for Application:{project_id} and License:{license_key}")
                    return JSONResponse(content={"message": "Incorrect Configuration Specified."}, status_code=500)
              else:
                  logger.error(f"Missing Invocation Id for Application:{project_id} and context:{context}")
                  return JSONResponse(content={"message": "Missing Invocation ID."}, status_code=500)                  
            else:
                logger.error(f"Missing or Incorrect context information Application:{project_id} and License:{license_key} and context:{context}")
                return JSONResponse(content={"message": "Missing or Incorrect context information."}, status_code=500)   
       else:
           logger.error(f"No Prompt found for Application:{project_id} and License:{license_key}")
           return JSONResponse(content={"message": "No prompt specified."}, status_code=500) 
    else:
         logger.error("Application or License key not found")
         return JSONResponse(content={"message": "Not allowed to use the specified configuration."}, status_code=401) 



#endregion


#region Anonymize
@app.post("/anonymize")
async def AnonymizeText(anonymizeReq : AnonymizeModel):  
    if anonymizeReq and anonymizeReq.projconfig and anonymizeReq.projconfig.key and anonymizeReq.projconfig.name: 
       project_id=anonymizeReq.projconfig.name
       license_key=anonymizeReq.projconfig.key
       context=anonymizeReq.context if anonymizeReq.context else ""
       if anonymizeReq.chunks:  
            if anonymizeReq.context and anonymizeReq.context.username and anonymizeReq.context.llm:     
              if anonymizeReq.invocation_id and anonymizeReq.invocation_type:  
                statrtime=time.time()           
                logger.info(f"Starting Anonymization")
                violationcount=PolicyViolationRepository.CheckPerUserViolation(anonymizeReq.context.username,project_id)
                logger.info(f"{violationcount} violations found in {time.time()-statrtime}")
                if violationcount>config_data["THRESHOLD_VIOLATION_COUNT"]:
                    return JSONResponse(content={ "AllowPrompt":False, "updatedPrompt":"You are blocked from accessing the LLMs due to too many Guardrail violations."}, status_code=200 )
                logger.info(f"Initiating Project Get")
                progetstart=time.time()   
                projectDetails= await ProjectPolicyDetailsRepository.ValidateLicense(project_id,license_key)
                logger.info(f"View Get Time {time.time()- progetstart}")
                validlicensetime=time.time()
                if projectDetails:
                    logger.info(f"in projectDetails {projectDetails}")
                    [PolicyMatched,chunks]=Anonymize(projectDetails,anonymizeReq.context,anonymizeReq.chunks,anonymizeReq.invocation_id,config_data["ANON-KEY"])
                    logger.info(f"Anonymization Runtime")
                    if PolicyMatched:
                        return JSONResponse(content=chunks, status_code=200 )
                    else:
                        logger.error(f"No Policy Matching specified LLM Found Project:{project_id} and License:{license_key} and context:{context}")
                        return JSONResponse(content={"message": "No Policy Matching specified LLM Found."}, status_code=500 )
                else:
                    logger.error(f"Application and License Key doesnt match for Application:{project_id} and License:{license_key}")
                    return JSONResponse(content={"message":   "Incorrect Configuration Specified."}, status_code=500 )
              else:
                  logger.error(f"Missing Invocation Id for Application:{project_id} and context:{context}")
                  return JSONResponse(content={"message":   "Missing Invocation ID."}, status_code=500 )
            else:
                logger.error(f"Missing or Incorrect context information Application:{project_id} and License:{license_key} and context:{context}")
                return JSONResponse(content={"message": "Missing or Incorrect context information."}, status_code=500 ) 
       else:
           logger.error(f"No Chunks found for Application:{project_id} and License:{license_key}")
           return JSONResponse(content={"message":   "No prompt specified."}, status_code=500 )
    else:
         logger.error("Application or License key not found")
         return JSONResponse(content={"message": "Not allowed to use the specified configuration."}, status_code=401 )

@app.post("/deanonymize")
async def DeAnonymizeText(deanonymizeReq : DeanonymizeModel):  
    if deanonymizeReq.projconfig and deanonymizeReq.projconfig.key and deanonymizeReq.projconfig.name: 
       project_id = deanonymizeReq.projconfig.name
       license_key = deanonymizeReq.projconfig.key
       context=deanonymizeReq.context if deanonymizeReq.context else ""
       if deanonymizeReq.text:  
            if deanonymizeReq.context and deanonymizeReq.context.username and deanonymizeReq.context.llm:     
              if deanonymizeReq.invocation_id and deanonymizeReq.invocation_type:  
                statrtime=time.time()           
                logger.info(f"Starting Anonymization")
                violationcount=PolicyViolationRepository.CheckPerUserViolation(deanonymizeReq.context.username,project_id)
                logger.info(f"{violationcount} violations found in {time.time()-statrtime}")
                if violationcount>config_data["THRESHOLD_VIOLATION_COUNT"]:
                    return JSONResponse(content={
                                "AllowPrompt":False,
                                "updatedPrompt":"You are blocked from accessing the LLMs due to too many Guardrail violations."
                            }, status_code=200 )
                logger.info(f"Initiating Project Get")
                progetstart=time.time()   
                projectDetails=await ProjectPolicyDetailsRepository.ValidateLicense(project_id,license_key)
                logger.info(f"View Get Time {time.time()- progetstart}")
                validlicensetime=time.time()
                if projectDetails:
                    [PolicyMatched,answer]=DeAnonymize(projectDetails,deanonymizeReq.context,deanonymizeReq.text,deanonymizeReq.invocation_id,config_data["ANON-KEY"])
                    if PolicyMatched:
                        responeObj={
                            "text":answer,
                        }
                        return JSONResponse(content=responeObj, status_code=200)
                    else:
                        logger.error(f"No Policy Matching specified LLM Found Application:{project_id} and License:{license_key} and context:{context}")
                        return JSONResponse(content={"message":   "No Policy Matching specified LLM Found."}, status_code=500 )
                else:
                    logger.error(f"Application and License Key doesnt match for Application:{project_id} and License:{license_key}")
                    return JSONResponse(content={"message":   "Incorrect Configuration Specified."}, status_code=500 )
              else:
                  logger.error(f"Missing Invocation Id for Application:{project_id} and context:{context}")
                  return JSONResponse(content={"message":   "Missing Invocation ID."}, status_code=500 )
            else:
                logger.error(f"Missing or Incorrect context information Application:{project_id} and License:{license_key} and context:{context}")
                return JSONResponse(content={"message":   "Missing or Incorrect context information."}, status_code=500 )
       else:
           logger.error(f"No Text found for Application:{project_id} and License:{license_key}")
           return JSONResponse(content={"message":   "No prompt specified."}, status_code=500 )
    else:
         logger.error("Application or License key not found")
         return JSONResponse(content={"message":   "Not allowed to use the specified configuration."}, status_code=401 )

#endregion


#region App Settings
@app.get("/getsettings")
def GetSettings(request: Request):  
     username = isAuthenticated(request)
     if username is None:
       return UnauthenticatedUserResponseReturn()
     constants= readfileAndGetData("constants") 
     approvalFlowKey=constants["AppSettings"]["APPROVAL_FLOW"]
     approve_setting=AppSettingsRepository.GetSettingValue(approvalFlowKey)
     returnObj={
         "approve_setting":approve_setting,
         "approveSettingList":constants["APPROVE_SETTING"]           
        }
     return JSONResponse(content=returnObj, status_code=200)

@app.post("/saveapprovalflow")
def SaveApprovalFlow(approvalflowReq : SaveApprovalflowModel , request: Request):
    username = isAuthenticated(request)
    if username is None:
       return UnauthenticatedUserResponseReturn()
    value=approvalflowReq.Value
    constants= readfileAndGetData("constants") 
    approvalFlowKey=constants.get("AppSettings")
    approvalFlowKey = approvalFlowKey.get("APPROVAL_FLOW")
    AppSettingsRepository.SaveSettings(approvalFlowKey,value)
    return JSONResponse(content={"success":True}, status_code=200)
#endregion

if __name__ == "__main__":
    uvicorn.run(
        "main:app"
    )