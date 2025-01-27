import signal
from utils.logger import logger
from masterctl import MasterCtl
from utils.cli import is_valid_cmd, print_short_help, print_large_help, parse_startup_args, valid_cmds
from utils.config import load_config, isValidConfig
import readline
from typing import List


def handle_sighup(sig, frame) -> None:
    """Handle the SIGHUP signal.
    Reload the configuration file"""
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




def select_cmd(cmd: str, args: List[str]) -> None:

    if input == "exit":
        master.exit(1)
    elif cmd == "help":
        print_large_help()
    if cmd == "start":
        master.start(args)
    elif cmd == "stop":
        master.stop(args)
    elif cmd == "restart":
        master.restart(args)
    elif cmd == "status":
        master.status(args)
    elif cmd == "avail":
        master.avail()
    elif cmd == "reload":
        master.reload()


def main_loop_ctl():

    init_signals()
    
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
            select_cmd(user_input.split()[0], user_input.split()[1:])


# log_level=DEBUG if not specified
def taskmaster() -> None:

    config_file, log_level = parse_startup_args()
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

    # refer to the existing global variable
    global master
    master = MasterCtl(config_file, config)
    logger.info(f"Taskmaster is running - pid: {master.pid}")
    
    master.init_services()
    main_loop_ctl()


master: MasterCtl = MasterCtl()


if __name__ == "__main__":
    taskmaster()
