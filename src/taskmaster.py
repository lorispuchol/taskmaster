import sys
import yaml
import readline
import argparse


from logger import logger

# TODO: Typed variable 

valid_cmds = {
    "start": "Start the mentionned program present in the configuration file",
    "stop": "Stop the mentionned program present in the configuration file",
    "restart": "Restart the mentionned program present in the configuration file",
    "status": "Displays the status of all the programs present in the configuration file",
    "exit": "Exit the main program",
    "help": "Display the list of valid commands with their description",
    "reload": "Reload the configuration (be careful to reload when configuration file changed. Otherwise, changes will be ignored)",
}


config: dict = {}
programs: list[dict] = []

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
        print(f"{cmd.ljust(max_cmd_length)}:\t {desc}")


def is_valid_cmd(cmd: str) -> bool:
    return cmd in valid_cmds


def recover_config_file(config_file: str) -> dict:
    """Parses a YAML configuration file into a dict.

    Args:
        config_file (str): The path to the YAML configuration file.

    Returns:
        dict: The parsed configuration.
    """
    with open(config_file, "r") as f:
        global config
        config = yaml.safe_load(f)
    print("Config file parsed successfully")
    logger.warning("Config file parsed successfully")
    return config


def is_valid_config(conf: dict):
    """
    Checks if the given configuration is valid.

    Args:
        conf (dict): The configuration to check.

    Raises:
        Exception: If the configuration is invalid.

    Returns:
        bool: True if the configuration is valid, False otherwise.
    """
    required_fields = ["programs"]

    if not conf:
        raise Exception("Config file is empty")
    if not isinstance(conf, dict):
        raise Exception("Config file must start by an object")
    for field in required_fields:
        if field not in conf:
            raise Exception(f"Config file is missing required field: {field}")
    if not isinstance(conf["programs"], dict):
        raise Exception("Config file 'programs' field must be an object")
    return True



def wait_for_cmds():
    while True:
        user_input: str = input("taskmaster> (type 'help'): ")

        if not user_input:
            continue

        readline.add_history(user_input)

        if not is_valid_cmd(user_input):
            print_short_help()
        elif user_input == "exit":
            print("Closing connection.")
            break
        elif user_input == "help":
            print_large_help()
        else:
            perform_cmd(user_input)


def perform_cmd(cmd: str):
    print(f"Performing command: {cmd}")


def taskmaster():

    parser = argparse.ArgumentParser(description="Taskmaster is a program that manages other programs.")
    parser.add_argument("filename", type=str, help="The path to the configuration file.",)
    parser.add_argument("-l", "--loglevel", help="Set the log level. INFO by default", action="store", default="INFO", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    
    args = parser.parse_args()

    logger.setLevel(args.loglevel.upper())

    print(args.loglevel)
    global config

    try:
        config = recover_config_file(sys.argv[1])
        is_valid_config(config)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)



if __name__ == "__main__":
    taskmaster()


# # Initialize the parser
# parser = argparse.ArgumentParser(description="A script to demonstrate arguments.")

# # Add arguments
# parser.add_argument("-n", "--name", type=str, required=True, help="Your name.")
# parser.add_argument("-a", "--age", type=int, help="Your age.")
# parser.add_argument("--verbose", action="store_true", help="Enable verbose mode.")

# # Parse arguments
# args = parser.parse_args()

# # Use the arguments
# if args.verbose:
#     print("Verbose mode is enabled.")
# print(f"Hello, {args.name}!")
# if args.age:
#     print(f"You are {args.age} years old.")
