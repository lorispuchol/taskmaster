import yaml, json
import argparse
import signal
import os
from logger import logger
from service import Service
from config import ConfValidator, isValidConfig


class Master:
    def __init__(
        self,
        pathToConfigFile: str = "",
        loggerLevel: str = "DEBUG",
        conf: dict = {},
    ):
        self.configFile = pathToConfigFile
        self.logLevel = loggerLevel
        self.fullconfig: dict = conf
        self.services: list[Service] = []
        self.pid: int = os.getpid()

    def _init_services(self):
        """
        Use to instanciate services classes into master class

        Also used at reload configuration because it check if the service is modified
        """

        # for service in self.fullconfig["programs"]:
        #     ServiceValidator.validate({service: self.fullconfig["programs"][service]})
        #     if not ServiceValidator.validate(self.fullconfig["programs"][service]):
        #         logger.error(f"Service {service} properties are invalid: {ServiceValidator.errors}")
        #         return False
            # return True

    def exit(exit_code: int) -> None:
        """
        Exit the taskmaster and all its programs.
        """
        # TODO: Stop all programs
        logger.info("Exiting taskmaster")
        exit(exit_code)


master = Master()


def handle_sigint(sig, frame) -> None:
    """Handle the SIGINT signal"""
    global master
    logger.warning("SIGINT Received")
    master.exit(130)


def handle_sigquit(sig, frame) -> None:
    """Handle the SIGQUIT signal."""
    global master
    logger.warning("SIGQUIT Received")
    master.exit(131)

def handle_sighup(sig, frame) -> None:
    """Handle the SIGHUP signal."""
    logger.info("SIGHUP Received")
    reload_config()


def init_signals() -> None:
    signal.signal(signal.SIGINT, handle_sigint)
    signal.signal(signal.SIGQUIT, handle_sigquit)
    signal.signal(signal.SIGHUP, handle_sighup)
    # TODO: Add signals is necessary ? (SIGTERM, SIGKILL, SIGUSR1, SIGUSR2 ?)


def reload_config() -> None:
    """
    Reload the configuration file.
    """
    logger.info("Reloading config...")
    tmp_conf = load_config(master.configFile)
    if not isValidConfig(tmp_conf):
        # TODO: do not exit but log error and unconsidered the new configuration
        logger.info("Exiting taskmaster")
        exit(1)
    # TODO: Update programs
    master.fullconfig = tmp_conf


def load_config(configFile: str) -> dict:
    """Parses a YAML configuration file into a dict.

    Args:
        configFile (str): The path to the YAML configuration file.

    Returns:
        dict: The parsed configuration.
    """
    with open(configFile, "r") as f:
        config: dict = yaml.safe_load(f)
    logger.info("Config file loading...")
    return config


# Parse the launching command
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
        help="Set the log level. DEBUG if not specified.",
        action="store",
        default="DEBUG",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    args = parser.parse_args()
    return args.filename, args.logLevel


# log_level=DEBUG if not specified
def taskmaster() -> int:

    global master

    config_file, log_level = kickoff()
    logger.setLevel(log_level)

    logger.info("Starting taskmaster")

    try:
        config = load_config(config_file)
    except Exception as e:
        logger.error(e)
        logger.info("Exiting taskmaster")
        exit(1)

    if not isValidConfig(config):
        logger.info("Exiting taskmaster")
        exit(1)

    # print(json.dumps(ConfValidator.document["programs"][0], indent=4))
    # print(json.dumps(ConfValidator.normalized(config)["programs"][0], indent=4))
    
    init_signals()

    master = Master(config_file, log_level, config)

    logger.info(f"Taskmaster is running - pid: {master.pid}")

    master._init_services()

    # master._run_services()
    # while True:
    #     pass
    # return 0


if __name__ == "__main__":
    taskmaster()
