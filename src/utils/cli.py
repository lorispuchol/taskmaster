from typing import Tuple
import argparse


def startup_parsing() -> Tuple[str, str]:
    """Parses the startup command arguments.

    Returns:
        Tuple[str, str]: The configuration file path and the log level.
        log level is set to "INFO" if not specified.
    """

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


valid_cmds = {
    "start": "Start the mentionned program present in the configuration file",
    "stop": "Stop the mentionned program present in the configuration file",
    "restart": "Restart the mentionned program present in the configuration file",
    "status": "Displays the status of all the services present in the configuration file",
    "avail": "Displays the list of available services present in the configuration file",
    "availx": "Displays the list of available services with their extended information",
    "availxl": "Displays the list of available services with their extended information ad default values",
    "help": "Display the list of valid commands with their description",
    "reload": "Reload the configuration (be careful to reload when configuration file change. Otherwise, changes will be ignored)",
    "exit": "Exit interactive controller",
    "shutdown": "Shutdown the server exiting gracefully all managed processes",
}


def print_short_help():
    """Prints the list of valid commands."""
    print("Valid commands:")
    for cmd in valid_cmds:
        print(f"\t{cmd}")


# get the command with the max length to align the description with other commands
def print_large_help():
    """Prints the list of valid commands with their description."""
    print("Valid commands:")
    max_cmd_length = max(len(cmd) for cmd in valid_cmds)
    for cmd, desc in valid_cmds.items():
        return (f"\t{cmd.ljust(max_cmd_length)}:\t {desc}")


def is_valid_cmd(cmd: str) -> bool:
    return cmd.split()[0] in valid_cmds
