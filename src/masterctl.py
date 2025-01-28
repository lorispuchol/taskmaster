from typing import List, Optional, Dict
import os
from service import Service
from utils.logger import logger
from utils.config import load_config, isValidConfig


class MasterCtl:
    def __init__(
        self,
        configPath: str = "",
        conf: Dict = {},
    ):
        self.configPath = configPath
        self.fullconfig: Dict = conf
        self.services: List[Service] = []
        self.pid: int = os.getpid()

    def init_services(self):
        """
        Use to instanciate services classes into master class

        Also used at reload configuration because it check if the service is modified
        """
        service: Dict
        for service in self.fullconfig["services"]:
            self.services.append(Service(service["name"], service))

    #################################
    # taskmaster controller commands
    #################################

    def exit(self, exit_code: int) -> None:
        """
        Exit taskmaster and all its programs.
        """
        # TODO: Stop all programs: exit properly
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
        service_dict: Dict[str, Service] = {
            service.name: service for service in self.services
        }

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

    def avail(self) -> None:
        """
        Display the list of available services.
        """
        print("Available services:")
        for service in self.services:
            print(f"\t{service.name}")

    def status(self, args: Optional[List[str]] = None) -> None:
        """
        Display the status of the mentionned service(s). All services if not specified
        """
        for service in self.services:
            print(f"{service.name}: {service.status}")

    def stop(self, args: Optional[List[str]] = None) -> None:
        """
        Stop the mentionned service(s). All services if not specified
        """
        # If no arguments are provided, then it perform action for all services
        if args is None or len(args) == 0:
            for service in self.services:
                service.stop()
            print("All services stopped")
            return

        # Create a dictionary for quick lookup of services by name (comprenhension dict). Service name's as key and Service object as value
        service_dict: Dict[str, Service] = {
            service.name: service for service in self.services
        }

        found_services = []
        not_found_services = []

        for arg in args:
            if arg in service_dict.keys():
                service_dict[arg].stop()
                found_services.append(arg)
            else:
                logger.warning(f"Service not found: {arg}")
                not_found_services.append(arg)

        # Optionally return or print a summary with 'found_services' and 'not_found_services'
        print(f"Services not found: {not_found_services}")

    def restart(self, args: Optional[List[str]] = None) -> None:
        """
        Restart the mentionned service(s). All services if not specified
        """
        # If no arguments are provided, then it perform action for all services
        if args is None or len(args) == 0:
            for service in self.services:
                service.restart()
            print("All services restarted")
            return

        # Create a dictionary for quick lookup of services by name (comprenhension dict). Service name's as key and Service object as value
        service_dict: Dict[str, Service] = {
            service.name: service for service in self.services
        }

        found_services = []
        not_found_services = []

        for arg in args:
            if arg in service_dict.keys():
                service_dict[arg].restart()
                found_services.append(arg)
            else:
                logger.warning(f"Service not found: {arg}")
                not_found_services.append(arg)

        # Optionally return or print a summary with 'found_services' and 'not_found_services'
        print(f"Services not found: {not_found_services}")
