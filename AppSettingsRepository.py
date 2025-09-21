import logging
import uuid
from repository.dbhandler import GetSession
from util import getCurrentDateTime
from repository.AppSettingsEntity import AppSettings
from repository.appgroupentity import AppGroup
from repository.projectentity import Project
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import and_,exists,func

class AppSettingsRepository:

    @staticmethod
    def GetSettingValue(setting_name):
         with GetSession() as session:
            try:
                setting=session.query(AppSettings).filter_by(setting_name=setting_name).first()
                if not setting ==None:
                    return setting.setting_value
                else:
                    return ""
            except Exception as e:
              
                logging.error(f"an error occurred: {e}")
                raise e
            finally:
                session.close()
                
    
    # @staticmethod
    # def GetSettingValueInternal(session,setting_name):
    #     try:
    #         setting=session.query(AppSettings).filter_by(setting_name=setting_name).first()
    #         if not setting ==None:
    #             return setting.setting_value
    #         else:
    #             return ""
    #     except Exception as e:
    #         logging.error(f"an error occurred: {e}")
    #         raise e
    #     finally:
    #         session.close()
    
    @staticmethod
    def SaveSettings(setting_name,value):
         with GetSession() as session:
            try:
               setting=session.query(AppSettings).filter_by(setting_name=setting_name).first()
               if setting:
                   setting.setting_value=value
                   session.commit()
            except Exception as e:
                session.rollback()
                logging.error(f"an error occurred: {e}")
                raise e
            finally:
                session.close()