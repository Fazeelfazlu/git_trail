import jwt
from logger import logger
from datareader import readfileAndGetData
from create_app import app,config_data
from keyvaultmanager import getKeyVaultSecret

def isAuthenticated(req):
    token = req.headers.get("x-access-token")
    logger.info(f"token {token}")
    if token is None:
        return None
    else:
        try:
            secret=getKeyVaultSecret(config_data["JWT-KEY"])
            decoded_token = jwt.decode(jwt=token,
                              key=secret,
                              algorithms=["HS256"])            
            username = decoded_token.get("username")
            
            return username
        except Exception as e:
            logger.error(f"Error in decocing token {e}")
            return None

def getuserrole(req):
    token = req.headers.get("x-access-token")
    logger.info(f"token {token}")
    if token is None:
        return (None,None)
    else:
        try:
            secret=getKeyVaultSecret(config_data["JWT-KEY"])
            decoded_token = jwt.decode(jwt=token,
                              key=secret,
                              algorithms=["HS256"])            
            username = decoded_token.get("username")          
            role = decoded_token.get("role")
            
            return (username,role)
        except Exception as e:
            logger.error(f"Error in decocing token {e}")
            return (None,None)
        

def AutheticateTuringPrompt(project_id,versionid,llm,token):   
    if token is None:
        return False
    else:
        try:
            secret=getKeyVaultSecret(config_data["JWT-KEY"])
            decoded_token = jwt.decode(jwt=token,
                              key=secret,
                              algorithms=["HS256"])            
            token_project_id = decoded_token.get("project_id")
            token_versionid = decoded_token.get("versionid")
            token_llm = decoded_token.get("llm")
            return token_project_id==project_id and versionid==token_versionid and llm==token_llm           
        except Exception as e:
            logger.error(f"Error in decoding Turing token {e}")
            return None