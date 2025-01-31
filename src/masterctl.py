from typing import List, Optional, Dict
import os
from service import Service
from utils.logger import logger
from utils.config import load_config, validateConfig


class MasterCtl:
    def __init__(
        self,
        configPath: str = "",
        conf: Dict = {},
    ):
        self.configPath = configPath
        self.fullconfig: Dict = conf
        self.services: Dict[str, Service] = {}  # {"name", Service}
        self.pid: int = os.getpid()

    def init_services(self):
        """
        Use to instanciate services classes into master class

        Also used at reload configuration because it check if the service is modified
        """
        for new_serv in self.fullconfig["services"]:
            name = new_serv["name"]
            self.services[name] = Service(name, new_serv)

    #################################
    # taskmaster controller commands
    #################################

    def avail(self) -> None:
        """
        Display available services.
        """
        print("Available services:")
        for serv in self.services.keys():
            print(f"\t{serv}")

    def exit(self, exit_code: int) -> None:
        """
        Exit taskmaster and all its programs.
        """
        for serv in self.services.values():
            print(*serv.stop(), sep="\n")
        logger.info("Exiting taskmaster")
        exit(exit_code)

    def status(self, args: Optional[List[str]] = None) -> None:
        """
        Display the status of the mentionned service(s). All services if not specified
        """
        if args is None or len(args) == 0 or (args[0] == "all" and len(args) == 1):
            for serv in self.services.values():
                print(*serv.status(), sep="\n")
            return
        else:
            for serv in self.services.values():
                if serv.name in args:
                    print(*serv.status(), sep="\n")


    def reload(self) -> None:
        """
        Reload the configuration file.
        """
        logger.info("Reloading...")

        try:
            new_conf = load_config(self.configPath)
            validateConfig(new_conf)
        except Exception as e:
            logger.warning(f"Failed to reload configuration: {e}")
            print(f"Failed to reload configuration\n{e}")
            return

        if new_conf == self.fullconfig:
            logger.info("Configuration didn't change")
            print("Configuration didn't change")
            return

        # New services or known services
        for new_props in new_conf["services"]:
            name = new_props["name"]
            # Known
            if new_props["name"] in self.services.keys():
                if new_props != self.services[name].props:
                    print(f"{name}: updated process group")
                    print(*self.services[name].reload(new_props), sep="\n")
            # New
            else:
                print(f"{name}: added process group")
                self.services[name] = Service(name, new_props)

        # List of services to remove
        services_to_remove: List[str] = [
            service.name
            for service in self.services.values()
            if service.name
            not in [new_props["name"] for new_props in new_conf["services"]]
        ]
        # Stop and remove the service
        for serv in services_to_remove:
            print(f"{serv}: removed process group")
            print(*self.services[serv].stop(), sep="\n")
            self.services.pop(serv)
        self.fullconfig = new_conf

    def start(self, args: Optional[List[str]] = None) -> str:
        """
        Start mentionned services. All services if not specified
        """
        if args is None or len(args) == 0 or (args[0] == "all" and len(args) == 1):
            for serv in self.services.values():
                print(*serv.start(), sep="\n")
            return
        for arg in args:
            if arg in self.services.keys():
                print(*self.services[arg].start(), sep="\n")
            else:
                logger.warning(f"Service not found: {arg}")
                print(f"Service not found: {arg}")

    def stop(self, args: Optional[List[str]] = None) -> str:
        """
        Stop mentionned services. All services if not specified
        """
        if args is None or len(args) == 0 or (args[0] == "all" and len(args) == 1):
            for serv in self.services.values():
                print(*serv.stop(), sep="\n")
            return
        for arg in args:
            if arg in self.services.keys():
                print(*self.services[arg].stop(), sep="\n")
            else:
                logger.warning(f"Service not found: {arg}")
                print(f"Service not found: {arg}")

    def restart(self, args: Optional[List[str]] = None) -> str:
        """
        Restart mentionned services. All services if not specified
        """
        if args is None or len(args) == 0 or (args[0] == "all" and len(args) == 1):
            for serv in self.services.values():
                print(*serv.restart(), sep="\n")
            return
        for arg in args:
            if arg in self.services.keys():
                print(*self.services[arg].restart(), sep="\n")
            else:
                logger.warning(f"Service not found: {arg}")
                print(f"Service not found: {arg}")
