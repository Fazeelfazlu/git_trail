from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import urllib
from repository.BaseEntity import Base
from create_app import app,config_data
from sqlalchemy.ext.declarative import declarative_base
# from keyvaultmanager import getKeyVaultSecret
# from sqlalchemy.pool import NullPool

# pwd=getKeyVaultSecret(config_data["PWD_NAME"])
# host=getKeyVaultSecret(config_data["HOST_NAME"])
# encoded_password = urllib.parse.quote(pwd)
# db_name=config_data["DB_NAME"]


# engine = create_engine(f'postgresql://{config_data["DB_USER"]}:{encoded_password}@{host}:{config_data["DB_PORT"]}/{db_name}', pool_size=10, max_overflow=20, pool_timeout=30, pool_recycle=3600)

# USER = "postgres.jcdmchuiwqnvdwvufvqo"
# PASSWORD = "EnshieldAi123%40"
# HOST = "aws-0-ap-south-1.pooler.supabase.com"
# PORT = "5432"
# DBNAME = "postgres"


USER = "postgres"
PASSWORD = "Fazeel%4011"
HOST = "localhost"
PORT = "5432"
DBNAME = "appdb"


engine = create_engine(f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}",echo=True)


Base.metadata.create_all(engine)

try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Failed to connect: {e}")

def GetSession():
    session = Session(engine)
    return session
    

 
# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session
# import urllib
# from repository.BaseEntity import Base
# from create_app import app,config_data
# from keyvaultmanager import getKeyVaultSecret
# from sqlalchemy.pool import NullPool

# pwd=getKeyVaultSecret(config_data["PWD_NAME"])
# host=getKeyVaultSecret(config_data["HOST_NAME"])
# encoded_password = urllib.parse.quote(pwd)
# db_name=config_data["DB_NAME"]


# engine = create_engine(f'postgresql://{config_data["DB_USER"]}:{encoded_password}@{host}:{config_data["DB_PORT"]}/{db_name}', pool_size=10, max_overflow=20, pool_timeout=30, pool_recycle=3600)

# Base.metadata.create_all(engine)


# def GetSession():
#     session = Session(engine)
#     return session
    



