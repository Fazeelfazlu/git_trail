import logging
import time
from logging.handlers import TimedRotatingFileHandler
from create_app import app,config_data

LOG_FILE_NAME=config_data['LOG_FILE_NAME']

logger = logging.getLogger("Application Log")
logger.setLevel(logging.INFO)  
formatter = logging.Formatter("%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s")
handler = TimedRotatingFileHandler(LOG_FILE_NAME,
                                    when="w6",
                                    interval=1,
                                    backupCount=5)
handler.setFormatter(formatter)
logger.addHandler(handler)