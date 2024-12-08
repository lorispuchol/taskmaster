import yaml
import argparse

from logger import logger

# TODO: Typed variable


class Master:
    def __init__(
        self, pathToConfigFile: str = "", loggerLevel: str = "DEBUG", conf: dict = {}
    ):
        self.configFile = pathToConfigFile
        self.logLevel = loggerLevel
        self.config: dict = conf
        self.programs: list[Program] = []


master = Master()


valid_cmds = {
    "start": "Start the mentionned program present in the configuration file",
    "stop": "Stop the mentionned program present in the configuration file",
    "restart": "Restart the mentionned program present in the configuration file",
    "status": "Displays the status of all the programs present in the configuration file",
    "exit": "Exit the main program",
    "help": "Display the list of valid commands with their description",
    "reload": "Reload the configuration (be careful to reload when configuration file changed. Otherwise, changes will be ignored)",
}


conf_required_fields = ["programs"]


def isValidConfig(conf: dict):
    """
    Checks if the given configuration is valid.

    Args:
        conf (dict): The configuration to check.

    Raises:
        Exception: If the configuration is invalid.

    Returns:
        bool: True if the configuration is valid, False otherwise.
    """

    if not conf:
        raise Exception("Config file is empty")
    if not isinstance(conf, dict):
        raise Exception("Config file must start by an object")
    for field in conf_required_fields:
        if field not in conf:
            raise Exception(f"Config file is missing required field: '{field}'")
    if not isinstance(conf["programs"], dict):
        raise Exception("Config file: 'programs' field must be an object")
    return True


def loadConfig(configFile: str) -> dict:
    """Parses a YAML configuration file into a dict.

    Args:
        configFile (str): The path to the YAML configuration file.

    Returns:
        dict: The parsed configuration.
    """
    with open(configFile, "r") as f:
        config: dict = yaml.safe_load(f)
    logger.info("Config file loaded successfully")
    return config


# Parse how taskmaster is launched
def kickoff() -> tuple[str, str]:
    parser = argparse.ArgumentParser(
        description="Taskmaster is a program that manages other programs."
    )
    parser.add_argument(
        "filename", type=str, help="The path to the configuration file."
    )
    parser.add_argument(
        "-l",
        "--logLevel",
        help="Set the log level. INFO if not specified.",
        action="store",
        default="INFO",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    args = parser.parse_args()
    return args.filename, args.logLevel


# logLevel: INFO if not specified
def taskmaster():

    global master

    configFile, logLevel = kickoff()
    logger.setLevel(logLevel)

    try:
        config = loadConfig(configFile)
        isValidConfig(config)
    except Exception as e:
        logger.error(e)
        logger.info("Exiting taskmaster")
        return 1

    master = Master(configFile, logLevel, config)


if __name__ == "__main__":
    taskmaster()
