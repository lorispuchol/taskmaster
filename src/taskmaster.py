import yaml, json
import argparse
import signal
import os, sys
from logger import logger
from service import Service
from config import ConfValidator, isValidConfig
# from inputctl import wait_for_inputctl
from typing import List, Optional, Dict, Any
from masterctl import MasterCtl
from utils.command_line import is_valid_cmd, print_short_help, print_large_help
from utils.config import load_config, isValidConfig
import readline


def handle_sighup(sig, frame) -> None:
    """Handle the SIGHUP signal."""
    logger.info("SIGHUP Received")
    master.reload()

def handle_sigint(sig, frame) -> None:
    """Handle the SIGINT signal"""
    # global keybord refer to the existing global variable (create it if not exist)
    global master
    logger.warning("SIGINT Received")
    master.exit(130)

def handle_sigquit(sig, frame) -> None:
    """Handle the SIGQUIT signal. Then call the exit method of master: MasterCtl instance."""
    # global keybord refer to the existing global variable (create it if not exist)
    global master
    logger.warning("SIGQUIT Received")
    master.exit(131)

def init_signals() -> None:
    signal.signal(signal.SIGINT, handle_sigint)
    signal.signal(signal.SIGQUIT, handle_sigquit)
    signal.signal(signal.SIGHUP, handle_sighup)
    # TODO: Add signals is necessary ? (SIGTERM, SIGKILL, SIGUSR1, SIGUSR2 ?)


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

def perform_cmd(cmd: str):
    # TODO Perform the command (through the master or program class ?)
    print(f"Performing command: {cmd}")

def wait_for_inputctl():
    while True:
        user_input: str = input("taskmaster> (type 'help'): ")

        if not user_input:
            continue

        readline.add_history(user_input)

        if not is_valid_cmd(user_input):
            print_short_help()
        elif user_input == "exit":
            # TODO: Exit taskmaster properly
            master.exit(1)
            pass
        elif user_input == "help":
            print_large_help()
        elif user_input.split()[0] == "start":
            master.start(user_input.split()[1:])
        else:
            perform_cmd(user_input)

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

    global master 
    master = MasterCtl(config_file, config)
    logger.info(f"Taskmaster is running - pid: {master.pid}")
    
    master.init_services()
    wait_for_inputctl()


master: MasterCtl = MasterCtl()


if __name__ == "__main__":
    taskmaster()
