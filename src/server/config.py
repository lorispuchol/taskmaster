import cerberus, yaml
from logger import logger
from service import StopSignals, AutoRestart
from typing import Dict

schemaConfig = {
    "services": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {
                "name": {
                    "type": "string",
                    "required": True,
                    "empty": False,
                    "regex": "^(?!all$)[A-Za-z0-9_-]+$",
                    "maxlength": 20,
                    "nullable": False,
                },
                "cmd": {
                    "type": "string",
                    "required": True,
                    "empty": False,
                    "nullable": False,
                    "maxlength": 100,
                },
                "numprocs": {
                    "type": "integer",
                    "min": 1,
                    "max": 9,  # 32
                    "nullable": False,
                },
                "autostart": {
                    "type": "boolean",
                    "nullable": False,
                },
                "starttime": {
                    "type": "integer",
                    "min": 0,
                    "max": 10,
                    "nullable": False,
                },
                "startretries": {
                    "type": "integer",
                    "min": 0,
                    "max": 10,
                    "nullable": False,
                },
                "autorestart": {
                    "type": "string",
                    "allowed": [v.value for v in AutoRestart],
                    "empty": False,
                    "nullable": False,
                },
                "exitcodes": {
                    "type": "list",
                    "schema": {
                        "type": "integer",
                        "min": 0,
                        "max": 255,
                        "nullable": False,
                    },
                    "empty": False,
                    "nullable": False,
                },
                "stopsignal": {
                    "type": "string",
                    "allowed": [v.value for v in StopSignals],
                    "empty": False,
                    "nullable": False,
                },
                "stoptime": {
                    "type": "integer",
                    "min": 0,
                    "max": 10,
                    "nullable": False,
                },
                "env": {
                    "type": "dict",  # need schema ?
                    "allow_unknown": True,
                    "valuesrules": {
                        "type": "string",
                        "empty": True,
                        "nullable": False,
                    },
                    "keysrules": {"type": "string", "empty": False, "nullable": False},
                    "empty": True,
                    "nullable": False,
                },
                "workingdir": {
                    "type": "string",
                    "empty": False,
                    "nullable": False,
                },
                "umask": {
                    # format 0o755 OR 0 OR 0o75 or 0755
                    "type": "integer",
                    "min": 0o0,
                    "max": 0o777,
                    "nullable": False,
                },
                "stdout": {
                    "type": "string",
                    "empty": False,
                    "nullable": False,
                },
                "stderr": {
                    "type": "string",
                    "empty": False,
                    "nullable": False,
                },
                # for bonus
                "user": {
                    "type": "string",
                    "empty": False,
                    "nullable": False,
                },
            },
        },
    },
}


ConfValidator = cerberus.Validator(schemaConfig)


def load_config(configPath: str) -> Dict:
    """Parses a YAML configuration file into a dict.

    Args:
        configPath (str): The path to the YAML configuration file.

    Returns:
        dict: The parsed configuration.
    """
    with open(configPath, "r") as f:
        config: Dict = yaml.safe_load(f)
    logger.info("Config file loading...")
    return config


def validateConfig(newConfig: Dict) -> None:
    """Parses a configuration file into a dict.

    Args:
        newConfig (dict): The new configuration

    Returns:
        bool: True if the configuration is valid, False otherwise.
    """
    logger.info("Config file parsing...")
    if ConfValidator.validate(newConfig):
        logger.info("Configuration file parsed successfully")
    else:
        logger.error(f"Config file corrupted: {ConfValidator.errors}")
        raise ValueError(f"Config file corrupted: {ConfValidator.errors}")
