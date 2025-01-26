from typing import List, Optional, Dict
import os
from service import Service
from logger import logger
import readline
from utils.config import load_config, isValidConfig
from utils.command_line import is_valid_cmd, print_short_help, print_large_help
from config import ConfValidator, isValidConfig


class MasterCtl:
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
        
        # If no arguments are provided, then it perform action for all services
        if args is None or len(args) == 0:
            for service in self.services:
                service.start()
            print("All services started")
            return
        
        # Create a dictionary for quick lookup of services by name (comprenhension dict). Service name's as key and Service object as value
        service_dict: Dict[str, Service] = {service.name: service for service in self.services}

        found_services = []
        not_found_services = []

        for arg in args:
            if arg in service_dict.keys():
                service_dict[arg].start()
                found_services.append(arg)
            else:
                logger.warning(f"Service not found: {arg}")
                not_found_services.append(arg)

        # Optionally return or print a summary with 'found_services' and 'not_found_services'
        print(f"Services not found: {not_found_services}")

    def reload(self) -> None:
        """
        Reload the configuration file.
        """
        logger.info("Reloading config...")
        tmp_conf = load_config(self.configPath)
        if not isValidConfig(tmp_conf):
            # TODO: do not exit but log error and unconsidered the new configuration
            logger.info("Exiting taskmaster")
            exit(1)
        # TODO: Update programs
        self.fullconfig = tmp_conf