import requests
import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
 
# Variables
key_vault_name = "keyvault-cin-enshield-ai"  # Replace with your Key Vault name
secret_name = "HOST-IP"          # Replace with your Secret name
resource = "https://vault.azure.net/"
metadata_url = "http://169.254.169.254/metadata/identity/oauth2/token"
 
# Fetch the token from the Managed Identity endpoint
def get_access_token(resource):
    params = {
        "api-version": "2018-02-01",
        "resource": resource
    }
   
    headers = {
        "Metadata": "true"
    }
 
    response = requests.get(metadata_url, headers=headers, params=params)
 
    if response.status_code == 200:
        token = response.json().get("access_token")
        return token
    else:
        raise Exception(f"Failed to obtain token: {response.status_code} {response.text}")
 
# Function to access Key Vault secret using the token
def get_key_vault_secret(token):
    key_vault_url = f"https://{key_vault_name}.vault.azure.net/secrets/{secret_name}?api-version=7.3"
    headers = {
        "Authorization": f"Bearer {token}"
    }
 
    response = requests.get(key_vault_url, headers=headers)
 
    if response.status_code == 200:
        secret_value = response.json().get("value")
        return secret_value
    else:
        raise Exception(f"Failed to access Key Vault secret: {response.status_code} {response.text}")
 
# Main workflow
try:
    # Get the access token
    access_token = get_access_token(resource)
    print("Access Token obtained successfully.")
 
    # Get the Key Vault secret using the obtained token
    secret_value = get_key_vault_secret(access_token)
    print(f"Secret Value: {secret_value}")
 
except Exception as e:
    print(f"An error occurred: {e}")
