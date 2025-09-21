import logging
from create_app import app, config_data
from opencensus.ext.azure.log_exporter import AzureLogHandler
from keyvaultmanager import getKeyVaultSecret

metriclogger = logging.getLogger("Metrics Logger")
metriclogger.setLevel(logging.INFO) 
instrumentation_conn_string=getKeyVaultSecret(config_data["INSTRUMENTATION_NAME"])
metriclogger.addHandler(AzureLogHandler(
    connection_string=instrumentation_conn_string)
)

def logInfo(logObj):
    properties = {'custom_dimensions': logObj}
    metriclogger.info(f"Guardrail Invoked with {logObj['prompt']}",extra=properties)