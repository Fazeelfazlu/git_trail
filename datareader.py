
import json

def readfileAndGetData(keyname):
      f = open('masterdata.json')
      data = json.load(f)
      return data[keyname]

