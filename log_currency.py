from os import path, remove
import logging
import logging.config
import json

logConfigFile = "log_config_currency.json"

with open(logConfigFile, 'r') as logging_configuration_file:
    config_dict = json.load(logging_configuration_file)

# If applicable, delete the existing log file to generate a fresh log file during each execution
if path.isfile(config_dict['handlers']['file_handler']['filename']):
    remove(config_dict['handlers']['file_handler']['filename'])

logging.config.dictConfig(config_dict)

# Log that the logger was configured
logger = logging.getLogger(__name__)
logger.info('Completed configuring logger()!')