#  File unused at the moment

import readline

valid_cmds = {
    "start": "Start the mentionned program present in the configuration file",
    "stop": "Stop the mentionned program present in the configuration file",
    "restart": "Restart the mentionned program present in the configuration file",
    "status": "Displays the status of all the programs present in the configuration file",
    "avail": "Displays the list of available programs present in the configuration file",
    "exit": "Exit the main program (taskmaster)",
    "help": "Display the list of valid commands with their description",
    "reload": "Reload the configuration (be careful to reload when configuration file changed. Otherwise, changes will be ignored)",
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
        print(f"{cmd.ljust(max_cmd_length)}:\t {desc}")


def is_valid_cmd(cmd: str) -> bool:
    return cmd in valid_cmds


def perform_cmd(cmd: str):
    # TODO Perform the command (through the master or program class ?)
    print(f"Performing command: {cmd}")


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