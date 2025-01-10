import yaml, json
import argparse
import signal
import os, sys
from logger import logger
from service import Service
from config import ConfValidator, isValidConfig
# from inputctl import wait_for_inputctl
from typing import List, Optional, Dict, Any
import readline
import inspect


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
    tmp_conf = load_config(master.configPath)
    if not isValidConfig(tmp_conf):
        # TODO: do not exit but log error and unconsidered the new configuration
        logger.info("Exiting taskmaster")
        exit(1)
    # TODO: Update programs
    master.fullconfig = tmp_conf


def load_config(configPath: str) -> dict:
    """Parses a YAML configuration file into a dict.

    Args:
        configPath (str): The path to the YAML configuration file.

    Returns:
        dict: The parsed configuration.
    """
    with open(configPath, "r") as f:
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
def taskmaster() -> None:

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

    init_signals()

    master = Master(config_file, log_level, config)
    logger.info(f"Taskmaster is running - pid: {master.pid}")
    
    master.init_services()
    wait_for_inputctl()

if __name__ == "__main__":
    taskmaster()
