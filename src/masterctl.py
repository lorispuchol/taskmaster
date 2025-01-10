from typing import List, Optional, Dict
import os
from service import Service
from logger import logger
import readline


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
            print(user_input)
            print(user_input.split()[0])
            print_short_help()
        elif user_input == "exit":
            # TODO: Exit taskmaster properly
            # print(inspect.signature(master.exit))
            master.exit(0)
        elif user_input == "help":
            print_large_help()
        elif user_input.split()[0] == "start":
            master.start(user_input.split()[1:])
        else:
            perform_cmd(user_input)


class Master:
    def __init__(
        self,
        configPath: str = "",
        conf: dict = {},
    ):
        self.configPath = configPath
        self.fullconfig: dict = conf
        self.services: list[Service] = []
        self.pid: int = os.getpid()

    def init_services(self):
        """
        Use to instanciate services classes into master class

        Also used at reload configuration because it check if the service is modified
        """
        for service in self.fullconfig["programs"]:
            self.services.append(Service(service["name"], service))

    def exit(self, exit_code: int) -> None:
        """
        Exit the taskmaster and all its programs.
        """
        # TODO: Stop all programs
        logger.info("Exiting taskmaster")
        exit(exit_code)

    def start(self, args: Optional[List[str]] = None) -> str:
        
        # If no arguments are provided, start all services
        if args is None or len(args) == 0:
            for service in self.services:
                logger.info(f"Starting service: {service.name}")
                service.start()
            print("All services started")
            return
        # Create a dictionary for quick lookup of services by name
        service_dict: Dict[str, Service] = {service.name: service for service in self.services}

        started_services = []
        not_found_services = []

        for arg in args:
            if arg in service_dict.keys():
                logger.info(f"Starting service: {arg}")
                service_dict[arg].start()
                started_services.append(arg)
            else:
                logger.warning(f"Service not found: {arg}")
                not_found_services.append(arg)

        # Optionally return a summary (if needed)
        print(f"Services not found: {not_found_services}")


master = Master()
