import signal
from utils.logger import logger
from masterctl import MasterCtl
from utils.cli import (
    is_valid_cmd,
    print_short_help,
    print_large_help,
    startup_parsing,
)
from utils.config import load_config, validateConfig
import readline
from typing import List

#####################
# Signal handlers
#####################


def handle_sighup(sig, frame) -> None:
    """Handle the SIGHUP signal.
    Reload the configuration file"""
    # 'global' refers to the existing global variable (create it if not exist)
    global master
    logger.info(f"SIGHUP Received on taskmaster, pid: {master.pid}")
    master.reload()


def handle_sigint(sig, frame) -> None:
    """Handle the SIGINT signal.
    Calls the exit method of masterctl"""
    # 'global' refers to the existing global variable (create it if not exist)
    global master
    logger.warning(f"SIGINT Received on taskmaster, pid: {master.pid}")
    master.exit(130)


def handle_sigquit(sig, frame) -> None:
    """Handle the SIGQUIT signal.
    Calls the exit method of masterctl"""
    # 'global' refers to the existing global variable (create it if not exist)
    global master
    logger.warning(f"SIGQUIT Received on taskmaster, pid: {master.pid}")
    master.exit(131)


def init_signals() -> None:
    signal.signal(signal.SIGINT, handle_sigint)
    signal.signal(signal.SIGQUIT, handle_sigquit)
    signal.signal(signal.SIGHUP, handle_sighup)
    # TODO: Add signals is necessary ? (SIGTERM, SIGKILL, SIGUSR1, SIGUSR2 ?)


#####################################
# taskmaster starter and main loop
#####################################


master: MasterCtl = MasterCtl()


def select_action(cmd: str, args: List[str]) -> None:
    if cmd == "exit":
        master.exit(1)
    if cmd == "help":
        print_large_help()
    if cmd == "start":
        master.start(args)
    if cmd == "stop":
        master.stop(args)
    if cmd == "restart":
        master.restart(args)
    if cmd == "status":
        master.status(args)
    if cmd == "avail":
        master.avail()
    if cmd == "availx":
        master.availX()
    if cmd == "availxl":
        master.availXL()
    if cmd == "reload":
        master.reload()


def main_loop_ctl():
    logger.info(f"Taskmaster is running - pid: {master.pid}")
    while True:
        try:
            user_input: str = input("taskmaster> (try 'help'): ")
        except EOFError:
            master.exit(1)
        if not user_input:
            continue
        readline.add_history(user_input)
        if not is_valid_cmd(user_input):
            print_short_help()
        else:
            select_action(user_input.split()[0], user_input.split()[1:])


def taskmaster() -> None:

    config_file, log_level = startup_parsing()  # log_level = "DEBUG" if not specified
    logger.setLevel(log_level)

    try:
        config = load_config(config_file)
        validateConfig(config)
    except Exception as e:
        logger.error(e)
        print(f"ERROR: failed to start taskmaster\n{e}")
        exit(1)

    # refer to the existing global variable
    global master
    master = MasterCtl(config_file, config)

    master.init_services()
    init_signals()
    main_loop_ctl()


if __name__ == "__main__":
    taskmaster()
