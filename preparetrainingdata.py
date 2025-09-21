import json
import random
import math
import random
import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from spacy.training import docs_to_json
from repository.entityrepository import EntityRepository
import numpy as np
from create_app import app,config_data
#connection_string = app.config['BLOB_CONNECTION_STRING']
container_name = config_data['CONTAINER_NAME']

def prepare_training_validation_data_for_spacy(training_validation_data, type):
    nlp = spacy.blank("en")
    db = DocBin()
    classes = training_validation_data.get('classes',[])
    annotations = training_validation_data.get('annotations',[]) 

    test_train_data = {"classes": classes,
                "annotations": annotations }


    for text, annot in tqdm(test_train_data['annotations']):
            doc = nlp.make_doc(text)
            ents = []
            for start, end, label in annot["entities"]:
                span = doc.char_span(start, end, label = label, alignment_mode = 'contract')
                if span is None:
                    pass
                else:
                    ents.append(span)
    
            doc.ents = ents
            db.add(doc)

    if type == "validate":
        db.to_disk("./validation_data.spacy")  
        #az_blob_upload(connection_string, container_name, "validation_data.spacy", "validation_data.spacy")      
    if type == "train":
        db.to_disk("./training_data.spacy")
        #az_blob_upload(connection_string, container_name, "training_data.spacy", "training_data.spacy")
    
def get_training_data_and_prepare_docbin(trainingtype):
    #response = requests.get(trainingsourceurl, params=trainingparam, headers=headers)
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
    
    response = {
        'classes':classes.tolist(),
        'annotations':annotations
    }

    if response:
        #request_data = json.dumps(response)
        if trainingtype == "T":         
            prepare_training_validation_data_for_spacy(response, "train")
            #EntityRepository.updatetrainedentities(trainingtype)
        elif trainingtype == "V":
            prepare_training_validation_data_for_spacy(response, "validate")
            #EntityRepository.updatetrainedentities(trainingtype)
    else:
        raise ValueError("no json found for training/validation")

