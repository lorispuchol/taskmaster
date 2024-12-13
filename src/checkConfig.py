from logger import logger

def is_valid_config(conf: dict) -> bool:
    """
    Checks if the given configuration is valid.
    Valid means: file not empty, file is a dict, file contains 'programs' field, 'programs' field is a dict and not empty 
    
    Does not check the service's properties.

    Args:
        conf (dict): The configuration to check.

    Returns:
        bool: True if the configuration is valid, False otherwise.
    """

    required_conf_fields = ["programs"]

    # Check if the config is valid with 'programs' field
    if not conf:
        logger.error("Config file is empty")
        return False
    if not isinstance(conf, dict):
        logger.error("Config file must start by an object. No list or string allowed")
        return False
    for field in required_conf_fields:
        if field not in conf:
            logger.error(f"Config file is missing required field: '{field}'")
            return False

    # Check if the 'programs' field is valid object
    if not isinstance(conf["programs"], dict) or not conf["programs"]:
        logger.error(
            "Config file: 'programs' field must be an object. No program to manage"
        )
        return False
    
    logger.info("Config updated successfully")
    return True

