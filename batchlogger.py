import logging
import time
from logging.handlers import TimedRotatingFileHandler

LOG_FILE_NAME="trainingbatch.log"

logger = logging.getLogger("Batch Log")
logger.setLevel(logging.INFO)   
formatter = logging.Formatter("%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s")
handler = TimedRotatingFileHandler(LOG_FILE_NAME,
                                    when="w6",
                                    interval=1,
                                    backupCount=5)
handler.setFormatter(formatter)
logger.addHandler(handler)





