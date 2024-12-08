import readline


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
