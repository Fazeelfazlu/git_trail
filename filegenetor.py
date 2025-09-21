
from hashlib import sha1
import json
import pickle 
import tempfile
import uuid
import os
import shutil
import zipfile
from logger import logger
from safeunpickler import safeunpickle

def GenerateConfigFile(projconfig):
    f = open('guardrailconfig.json')
    data = json.load(f)
    data["projectdetails"]=projconfig
    logger.info(f"at generateconfig data- {data}")
    fingerprint= sha1(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()
    data["fingerprint"]=fingerprint
    fp=tempfile.NamedTemporaryFile(mode='w')
    tempfilename=fp.name
    with open(tempfilename, "wb") as filewriter:
         pickle.dump(data, filewriter)
    with open(tempfilename, 'rb') as fr:
            yield from fr

def GenerateExportFile(exportdata):
    fingerprint= sha1(json.dumps(exportdata, sort_keys=True).encode("utf-8")).hexdigest()
    exportdata["fingerprint"]=fingerprint
    fp=tempfile.NamedTemporaryFile(mode='w')
    tempfilename=fp.name
    with open(tempfilename, "wb") as filewriter:
         pickle.dump(exportdata, filewriter)
    with open(tempfilename, 'rb') as fr:
             yield from fr
    
def GenerateTextFile(data):
    fp=tempfile.NamedTemporaryFile(mode='w')
    tempfilename=fp.name
    with open(tempfilename, "w") as filewriter:
         filewriter.write(data)
    with open(tempfilename, 'r') as fr:
            yield from fr
    
def GetImportedFileData(file):
      filename = str(uuid.uuid4())
      with open(filename, "wb") as filewriter:
        data=file.read()
        filewriter.write(data)
      with open(filename, 'rb') as f:
        importeddata = safeunpickle(f.read())
      os.remove(filename)
      if validateFile(importeddata):
          projects=importeddata['projects']
          topics=importeddata['topics']
          env=importeddata['env']         
          return (0,[projects,topics,env])
      else:
          return (1,None)



def validateFile(data):
    contentValidtor=data["fingerprint"]
    del data['fingerprint'] 
    filedata= sha1(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()
    return filedata==contentValidtor


def ExportModelFile(modeldata,modelPath,statusFilePath,zipFilePath):
     if not os.path.isdir(modelPath):
          return 0
     else: 
        exportDirectory=modelPath+ "_export"
        if os.path.exists(exportDirectory):  
                 shutil.rmtree(exportDirectory)
        shutil.copytree(modelPath, exportDirectory)
        fingerprint= sha1(json.dumps(modeldata, sort_keys=True).encode("utf-8")).hexdigest()
        modeldata["fingerprint"]=fingerprint   
        filename= f"{exportDirectory}/{statusFilePath}" 
        with open(filename, "wb") as filewriter:
            pickle.dump(modeldata, filewriter)
        if os.path.exists(f"{zipFilePath}.zip"):
            os.remove(f"{zipFilePath}.zip")
        shutil.make_archive(zipFilePath, 'zip', exportDirectory)
        with open(f"{zipFilePath}.zip", 'rb') as fr:
                 yield from fr

def CheckModelExists(modelPath):
     if not os.path.isdir(modelPath):
          return 0
     else:
          return 1
     
def ExtractModelFile(modelZip,modelPath,statusFilePath):
      extractDirectory=f"{modelPath}_extract"
      if os.path.exists(extractDirectory):  
            shutil.rmtree(extractDirectory)
      with zipfile.ZipFile(modelZip, 'r') as zip_ref:
            zip_ref.extractall(extractDirectory)
      filename= f"{extractDirectory}/{statusFilePath}" 
      with open(filename, 'rb') as f:
          importeddata = safeunpickle(f.read())
      os.remove(filename)
      if validateFile(importeddata):           
          return (0,importeddata)
      else:
          return (1,None)

def CopyModel(modelPath):
    if os.path.exists(modelPath):  
        shutil.rmtree(modelPath) 
    extractDirectory=f"{modelPath}_extract"
    shutil.copytree(extractDirectory, modelPath)


def DeleteExtractedFile(modelPath):
      extractDirectory=f"{modelPath}_extract"
      if os.path.exists(extractDirectory):  
            shutil.rmtree(extractDirectory)
