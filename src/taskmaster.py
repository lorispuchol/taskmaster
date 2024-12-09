import yaml
import argparse
import signal

from logger import logger

# TODO: Typed variable


class Master:
    def __init__(
        self,
        pathToConfigFile: str = "",
        loggerLevel: str = "DEBUG",
        conf: dict = {}
    ):
        self.configFile = pathToConfigFile
        self.logLevel = loggerLevel
        self.config: dict = conf
        self.programs: list[Program] = []


master = Master()


def exit_taskmaster() -> None:
    # TODO : Stop all programs
    logger.info("Exiting taskmaster")
    exit(1)

def reload_config() -> None:
    logger.info("Reloading config")
    tmp_conf = load_config(master.configFile)
    if not is_valid_config(tmp_conf):
        logger.info("Exiting taskmaster")
        exit(1)
    # TODO : Update programs
    master.config = tmp_conf

def handle_sigint(sig, frame) -> None:
    logger.warning("Received SIGINT")
    exit_taskmaster()

def handle_sighup(sig, frame) -> None:
    logger.info("Received SIGHUP")
    reload_config()


def init_signals() -> None:
    signal.signal(signal.SIGINT, handle_sigint)
    signal.signal(signal.SIGHUP, handle_sighup)



def is_valid_config(conf: dict) -> bool:
    """
    Checks if the given configuration is valid.

    Args:
        conf (dict): The configuration to check.

    Raises:
        Exception: If the configuration is invalid.

    Returns:
        bool: True if the configuration is valid, False otherwise.
    """

    conf_required_fields = ["programs"]

    # Check if the config is valid with 'programs' field
    if not conf:
        logger.error("Config file is empty")
        return False
    if not isinstance(conf, dict):
        logger.error("Config file must start by an object. No list or string allowed")
        return False
    for field in conf_required_fields:
        if field not in conf:
            logger.error(f"Config file is missing required field: '{field}'")
            return False

    # Check if the 'programs' field is valid object
    if not isinstance(conf["programs"], dict) or not conf["programs"]:
        logger.error("Config file: 'programs' field must be an object. No program to manage")
        return False

    # if not conf["programs"]:
    #     raise Exception("Config file: 'programs' field must not be empty")
    # if not all(isinstance(program, dict) for program in conf["programs"].values()):
    #     raise Exception("Config file: 'programs' field must contain only objects")

    logger.info("Config updated successfully")
    return True


def load_config(configFile: str) -> dict:
    """Parses a YAML configuration file into a dict.

    Args:
        configFile (str): The path to the YAML configuration file.

    Returns:
        dict: The parsed configuration.
    """
    with open(configFile, "r") as f:
        config: dict = yaml.safe_load(f)
    logger.info("Config file updating...")
    print(config)
    return config


# Parse taskmaster's launching command
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


# log_level=INFO if not specified
def taskmaster() -> int:

    global master

    config_file, log_level = kickoff()
    logger.setLevel(log_level)

    logger.info("Taskmaster started")

    try:
        config = load_config(config_file)
    except Exception as e:
        logger.error(e)
        logger.info("Exiting taskmaster")
        return 1

    if not is_valid_config(config):
        logger.info("Exiting taskmaster")
        return 1
    
    init_signals()

    master = Master(config_file, log_level, config)
    while True:
        pass
    return 0

if __name__ == "__main__":
    taskmaster()
