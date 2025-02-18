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
import sys
import select
from process import State
import subprocess


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


def maintain_processes():
    # return
    for service in master.services.values():
        for process in service.processes:
            if process.proc is not None and process.proc.poll() is not None:
                if service.autorestart and process.graceful_stopped == False:
                    print(f"Process {process.proc.pid} exited. Restarting...")
                    try:
                        process.start()
                    except Exception as e:
                        print(f"Error restarting process: {e}")
                        # managed_processes.remove(entry)
                        continue
                    # entry["proc"] = new_proc
                # else:
                    # managed_processes.remove(entry)
                    # print(f"Removed exited process {proc.pid}")

def main_loop():
    """
    Main loop of the taskmasterctl.
    It waits for user input and calls the appropriate method.
    It also iterates over the services and checks their status every second if their is no input
    """

    timeout: bool = False
    while True:
        if timeout == False:
            sys.stdout.write("taskmaster> (try 'help'): ")  # Display prompt
            sys.stdout.flush()
        rlist, _, _ = select.select([sys.stdin], [], [], 1.0)
        if rlist:
            timeout = False
            line = sys.stdin.readline().strip()
            if not line:
                continue
            if not is_valid_cmd(line):
                print_short_help()
            else:
                select_action(line.split()[0], line.split()[1:])
        else:   
            timeout = True
            maintain_processes()


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
    main_loop()


if __name__ == "__main__":
    taskmaster()
