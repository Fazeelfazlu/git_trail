import subprocess
import uuid
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
from repository.trainingstatusentity import TrainingStatusEntity
from repository.appgrouprepository import AppgroupRepository
from repository.AppSettingsRepository import AppSettingsRepository
from repository.promptrepository import PromptRepository
from repository.versionrepository import VersionRepository


from util import getCurrentDateTime
from preparetrainingdata import get_training_data_and_prepare_docbin
from datareader import readfileAndGetData
import os
from util import final_training_score
from batchlogger import logger
constants = readfileAndGetData('constants')

def starttraining():
    try:
        latest_status = TrainingStatusRepository.getlateststatus()
        if latest_status != constants['MODEL_TRAIN_STATUS']['TRAIN_PROGRESS']:
            if latest_status == constants['MODEL_TRAIN_STATUS']['TRAIN_INIT']:
                TrainingStatusRepository.updatetrainingprogress()
                get_training_data_and_prepare_docbin('T')
                get_training_data_and_prepare_docbin('V')
                outputfilename=constants["FILE_PATHS"]["OUTPUTFILE"]
                if os.path.exists(outputfilename):
                    os.remove(outputfilename)


                process = subprocess.run([' /bin/bash ./train.sh'], shell=True, check=True)
                if process.returncode == 0:
                    score=final_training_score(outputfilename)
                    obj_training_status = TrainingStatusEntity(
                        modified_by = TrainingStatusRepository.gettriggeredbyuser(),
                        training_status = constants['MODEL_TRAIN_STATUS']['TRAIN_SUCCESS'],
                        run_id = str(uuid.uuid4()),
                        f1_score = score
                    )
                    TrainingStatusRepository.update(obj_training_status)
                    EntityRepository.UpdateTrainingCompleted()
                else:
                    obj_training_status = TrainingStatusEntity(
                        modified_by = TrainingStatusRepository.gettriggeredbyuser(),
                        training_status = constants['MODEL_TRAIN_STATUS']['TRAIN_FAILURE'],
                        run_id = str(uuid.uuid4())
                    )
    except Exception as e:
        logger.error(f"Error Occured :{e}")
        obj_training_status = TrainingStatusEntity(
            modified_by = TrainingStatusRepository.gettriggeredbyuser(),
            training_status = constants['MODEL_TRAIN_STATUS']['TRAIN_FAILURE'],
            run_id = str(uuid.uuid4())
        )
        TrainingStatusRepository.update(obj_training_status)        
        raise Exception("training failed")


starttraining()