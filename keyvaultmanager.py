
from azure.keyvault.secrets import SecretClient
##from azure.identity import DefaultAzureCredential
from azure.identity import ManagedIdentityCredential
from create_app import app,config_data
import logging
#Configure logging
logging.basicConfig(level=logging.INFO)

keyVaultName = config_data['KEYVAULT_NAME']
KVUri = f"https://{keyVaultName}.vault.azure.net"

##credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
credential = ManagedIdentityCredential()
client = SecretClient(vault_url=KVUri, credential=credential)

##Function gets the Key value from the Keyvault
##access is based on the managed identity of the function app
def getKeyVaultSecret(secretName):
   
    retrieved_secret = client.get_secret(secretName)
    return retrieved_secret.value
