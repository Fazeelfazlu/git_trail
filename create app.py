
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json



app = FastAPI()
      

with open("config.json", "r") as config_file:
        config_data = json.load(config_file)

origins=config_data["ORIGIN"].split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['GET','POST','DELETE','HEAD','OPTIONS'],
    allow_headers=["*"],
)
