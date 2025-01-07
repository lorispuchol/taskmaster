import cerberus
from logger import logger
from enum import Enum
from service import StopSignalsValues, AutoRestartValues

schemaList = {
    'programs': {
        'type': 'list',
        'required': True,
        "schema": {
            "type": "dict",
            "schema": {
                "name": {
                    "type": "string",
                    "required": True,
                    'empty': False,
                },
                "cmd": {
                    "type": "string",
                    "required": True,
                    'empty': False,
                },
                "numprocs": {
                    "type": "integer",
                    "min": 1,
                    "max": 32,
                    "default": 1,
                },
                "autostart": {
                    "type": "boolean",
                    "default": True,
                },
                "starttime": {
                    "type": "integer",
                    "min": 0,
                    "default": 1,
                },
                "startretries": {
                    "type": "integer",
                    "min": 1,
                    "max": 10,
                    "default": 3,
                },
                "autorestart": {
                    "type": "string",
                    "allowed": [v.value for v in AutoRestartValues],
                    "default": AutoRestartValues.UNEXPECTED.value,
                },
                "exitcodes": {
                    "type": "list",
                    "schema": {
                        "type": "integer",
                        "min": 0,
                        "max": 255,
                    },
                    "default": [0], # success exit code
                },
                "stopsignal": {
                    "type": "string",
                    "allowed": [v.value for v in StopSignalsValues],
                    "default": StopSignalsValues.TERM.value,
                },
                "stoptime": {
                    "type": "integer",
                    "min": 0,
                    "default": 10,
                },
                "env": {
                    "type": "dict",
                },
                "workingdir": {
                    "type": "string",
                    "empty": False,
                },
                "umask": {
                    "type": "integer",
                    "min": 0o0,
                    "max": 0o777,
                },
                "stdout": {
                    "type": "string",
                },
                "stderr": {
                    "type": "string",
                },
                "user": {
                    "type": "string",
                },
            },
        },
    },
}

ConfValidator = cerberus.Validator(schemaList)

def isValidConfig(newConfig: dict) -> bool :
    """Parses a configuration file into a dict.

    Args:
        newConfig (dict): The new configuration

    Returns:
        bool: True if the configuration is valid, False otherwise.
    """
    logger.info("Config file parsing...")
    if ConfValidator.validate(newConfig):
        logger.info("Configuration file parsed successfully")
        return True
    logger.error(f"Config file corrupted: {ConfValidator.errors}")
    return False