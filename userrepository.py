from repository.UserEntity import User
from repository.usereventlogentity import UserEventLog
from repository.usersettingsentity import UserSettings
import logging
from util import getCurrentDateTime,encryptPass,decryptPass
from repository.dbhandler import GetSession
from sqlalchemy.sql import exists,and_,func
import pyotp 
from datareader import readfileAndGetData
from sqlalchemy.orm import joinedload 
from repository.admineventlogentity import AdminEventLog
from logger import logger

class UserRepository:
    @staticmethod
    def create(userobj, created_by,defaultpwd):
      with GetSession() as session:
        try:    
          if(UserRepository.validateUser(session,userobj.username,0)):
             return 2
          # pwd=hashlib.md5(defaultpwd.encode()).hexdigest()
          user = User(
              username=userobj.username,
              firstname=userobj.firstname,
              lastname=userobj.lastname,
              user_role=userobj.user_role,
              password=defaultpwd,
              active="Y",
              locked="N",
              is_two_factor_enabled="N",
              is_two_factor_required="Y",
              secret_token=pyotp.random_base32(),
              modified_by=created_by,
              modified_on=getCurrentDateTime(),
              created_by=created_by,
              created_on=getCurrentDateTime(),
              required_pwd_change = "Y"
          )
          session.add(user)
          session.commit()
          return 0
        except Exception as e:
            session.rollback()
            raise e
        finally:
           session.close()

    @staticmethod
    def read(userid):
         with GetSession() as session:
            try:  
              return session.query(User).filter_by(id=userid).first()
            except Exception as e:
                raise e
            finally:
               session.close()
    
    @staticmethod
    def readall():
         with GetSession() as session:
            try:  
               return session.query(User).order_by(User.created_on).all()
            except Exception as e:
                raise e
            finally:
               session.close()
       
    @staticmethod
    def update( userobj, id, modified_by):
      with GetSession() as session:
        try:       
          user = session.query(User).filter_by(id=id).first()
          if user:
              user.firstname=userobj.firstname
              user.lastname=userobj.lastname 
              user.user_role=userobj.user_role    
              user.modified_by = modified_by        
              user.modified_on = getCurrentDateTime()
              
              constants= readfileAndGetData("constants") 
              log = UserEventLog(event_name = constants["USER_EVENTS"]["USER_UPDATE"], 
                                  created_on = getCurrentDateTime(),
                                  created_by = modified_by)
              user.eventlogs.append(log)
              session.commit()
              return 0
          return 1
        except Exception as e:
          session.rollback()
          raise e
        finally:
           session.close()

    @staticmethod
    def deactivate( id, modified_by):
      with GetSession() as session:
        try:       
          user = session.query(User).filter_by(id=id).first()
          if user:             
              user.active="N"
              user.modified_by = modified_by        
              user.modified_on = getCurrentDateTime()
              
              constants= readfileAndGetData("constants")
              log = UserEventLog(event_name = constants["USER_EVENTS"]["DEACTIVATE"], 
                              created_on = getCurrentDateTime(),
                              created_by = modified_by)
              user.eventlogs.append(log)
              
              session.commit()
              return 0
          return 1
        except Exception as e:
          session.rollback()
          raise e
        finally:
           session.close()

    @staticmethod
    def activate( id, modified_by):
      with GetSession() as session:
        try:       
          user = session.query(User).filter_by(id=id).first()
          if user:             
              user.active="Y"
              user.modified_by = modified_by        
              user.modified_on = getCurrentDateTime()
              
              constants= readfileAndGetData("constants")
              log = UserEventLog(event_name = constants["USER_EVENTS"]["ACTIVATE"], 
                              created_on = getCurrentDateTime(),
                              created_by = modified_by)
              user.eventlogs.append(log)
              
              session.commit()
              return 0
          return 1
        except Exception as e:
          session.rollback()
          raise e
        finally:
           session.close()

    @staticmethod
    def unlock( id, modified_by):
      with GetSession() as session:
        try:       
          user = session.query(User).filter_by(id=id).first()
          if user:             
              user.locked="N"
              user.lockeddatetime=None
              user.incorrect_attempt=0
              user.modified_by = modified_by        
              user.modified_on = getCurrentDateTime()
              
              constants= readfileAndGetData("constants")
              log = UserEventLog(event_name = constants["USER_EVENTS"]["UNLOCK"], 
                              created_on = getCurrentDateTime(),
                              created_by = modified_by)
              user.eventlogs.append(log)
              
              session.commit()
              return 0
          return 1
        except Exception as e:
          session.rollback()
          raise e
        finally:
           session.close()

    @staticmethod
    def authenticate(username,pwd,incorrectLoginBlockCount):
      with GetSession() as session:
        try:     
          user = session.query(User).filter(func.lower(User.username)==func.lower(username),User.active=="Y",User.locked=="N").first()
          if user:  
            isPassTrue = decryptPass(user.password,pwd)            
            if not isPassTrue:
              return (1,None)
            else:
              if user.is_two_factor_required=="N":
                    user.incorrect_attempt=0
                    user.lastlogintime=getCurrentDateTime() 
                    session.commit()    
              if isPassTrue:
                user=session.query(User).filter(func.lower(User.username)==func.lower(username),User.active=="Y",User.locked=="N").first()      
                return (0,user) # valid Login
          else:
             user = session.query(User).filter(func.lower(User.username)==func.lower(username)).first()
              
             if user:
                if user.locked=="Y":
                  
                   return (2,None) #User Locked
                elif user.active=="N":
                  
                   return (3,None) #User Inactive
                else:
                   ##Incorrect Attempt
                   incorrect_attempt=user.incorrect_attempt
                   if not incorrect_attempt:
                      incorrect_attempt=0
                   incorrect_attempt+=1
                   locked="N"
                   if incorrect_attempt>=incorrectLoginBlockCount :
                         user.locked="Y"
                         user.lockeddatetime=getCurrentDateTime() 
                         constants= readfileAndGetData("constants")
                         log = UserEventLog(event_name = constants["USER_EVENTS"]["LOCKED"], 
                              created_on = getCurrentDateTime(),
                              created_by = username)
                         user.eventlogs.append(log)
                   user.incorrect_attempt=incorrect_attempt
                  
                   session.commit()
                   return (1,None)
             else:
                return (1,None)
        except Exception as e:
          session.rollback()
          raise e
        finally:
           session.close()

    @staticmethod
    def validateUser(session,username,userid):
       username=username.strip()
       return session.query(exists().where(and_(User.id != userid),(func.lower(User.username)==func.lower(username)))).scalar()
    
    @staticmethod
    def recordLastLogin(username):
      with GetSession() as session:
        try:       
          user = session.query(User).filter(func.lower(User.username)==func.lower(username)).first()
          user.incorrect_attempt=0
          if user.is_two_factor_enabled=="N":
             user.is_two_factor_enabled="Y"
          user.lastlogintime=getCurrentDateTime() 
          session.commit()  
        except Exception as e:
          session.rollback()
          raise e
        finally:
           session.close()

    @staticmethod
    def getuserfromusername(username):
      with GetSession() as session:
            try:  
              return session.query(User).filter(func.lower(User.username)==func.lower(username)).options(joinedload(User.settings)).first()
            except Exception as e:
                raise e
            finally:
               session.close()

    @staticmethod
    def changepwd( username,pwd,newpwd, incorrectLoginBlockCount):
      with GetSession() as session:
        try:       
          user = session.query(User).filter(func.lower(User.username)==func.lower(username),User.active=="Y",User.locked=="N").first()
          if user:  
            isPassTrue = decryptPass(user.password,pwd)            
            if not isPassTrue:
              return 1
            else:              

              newpwd = encryptPass(newpwd)
              
              constants= readfileAndGetData("constants")               
              user.password=newpwd     
              user.required_pwd_change="N"
              log = UserEventLog(event_name = constants["USER_EVENTS"]["CHANGE_PWD"], 
                                  created_on = getCurrentDateTime(),
                                  created_by = username)
              user.eventlogs.append(log)
              session.commit()        
              return 0 # valid Login
          else:
             user = session.query(User).filter(func.lower(User.username)==func.lower(username)).first()
             if user:
                if user.locked=="Y":
                   return 2 #User Locked
                elif user.active=="N":
                   return 3 #User Inactive
                else:
                   ##Incorrect Attempt
                   incorrect_attempt=user.incorrect_attempt
                   if not incorrect_attempt:
                      incorrect_attempt=0
                   incorrect_attempt+=1
                   locked="N"
                   if incorrect_attempt>=incorrectLoginBlockCount :
                         user.locked="Y"
                         user.lockeddatetime=getCurrentDateTime() 
                         log = UserEventLog(event_name = constants["USER_EVENTS"]["LOCKED"], 
                                created_on = getCurrentDateTime(),
                                created_by = username)
                         user.eventlogs.append(log)
                   user.incorrect_attempt=incorrect_attempt
                 
                   session.commit()
                   return 1
             else:
                return 1
        except Exception as e:
          session.rollback()
          raise e
        finally:
           session.close()

    @staticmethod
    def resetpwd(username,pwd):
      with GetSession() as session:
        try:       
          user = session.query(User).filter(func.lower(User.username)==func.lower(username),User.active=="Y").first()
          if user:  
             constants= readfileAndGetData("constants") 
             pwd = encryptPass(pwd)
             
             user.password=pwd     
             log = UserEventLog(event_name = constants["USER_EVENTS"]["RESET_PWD"], 
                                created_on = getCurrentDateTime(),
                                created_by = username)
             user.eventlogs.append(log)
             session.commit()        
             return 0 # reseted
        except Exception as e:
          session.rollback()
          raise e
        finally:
           session.close()


    @staticmethod
    def saveSettings(username,settingsObj):
      with GetSession() as session:
        try:       
          user = session.query(User).filter(func.lower(User.username)==func.lower(username)).first()
          if user:
             usersetting=session.query(UserSettings).filter(and_(UserSettings.userid==user.id),(UserSettings.setting_name==settingsObj.settingname)).first()
             if usersetting:
                usersetting.setting_value=settingsObj.settingvalue
             else:
                usersetting=UserSettings(
                   setting_name=settingsObj.settingname,
                   setting_value=settingsObj.settingvalue,
                   created_on=getCurrentDateTime(),
                   created_by=username

                )
                user.settings.append(usersetting)             
             session.commit()  
             return 0
          return 1
        except Exception as e:
          session.rollback()
          raise e
        finally:
           session.close()
           
    @staticmethod
    def loguserhandelsearch(username,modifiedBy):
      with GetSession() as session:
            try: 
              constants= readfileAndGetData("constants")
              log = AdminEventLog(eventname = constants["ADMIN_EVENTS"]["USER_DEANON"],
                                project_id = "",
                                new_value = username,
                                created_by = modifiedBy,
                                created_on = getCurrentDateTime(),
                                prev_value = ""
                                )
              session.add(log)  
              session.commit() 
            except Exception as e:
                raise e
            finally:
              session.close()