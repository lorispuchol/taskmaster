import os
from typing import List, Optional, Dict
from service import Service
from logger import logger
from config import load_config, validateConfig
from utils.colors import Color


class MasterCtl:
    def __init__(
        self,
        configPath: str = "",
        conf: Dict = {},
    ):
        self.configPath = configPath
        self.fullconfig: Dict = conf
        self.services: Dict[str, Service] = {}  # {"name": Service}
        self.pid: int = os.getpid()

    def init_services(self) -> None:
        """
        Use to instanciate services
        Accept only the last defined service if the service is defined multiple times
        """
        # If a service is defined multiple times, only the last definition will be retained
        i: int = 1
        for new_serv in self.fullconfig["services"]:
            name = new_serv["name"]
            if name not in self.services.keys() and name not in [
                serv["name"] for serv in self.fullconfig["services"][i:]
            ]:
                self.services[name] = Service(name, new_serv)
            i += 1

    ###############################
    # taskmaster control commands #
    ###############################

    def avail(self) -> str:
        """
        Display available services.
        """
        messages: List[str] = []
        messages.append("Available services:")
        for serv in self.services.keys():
            messages.append(Color.BOLD + f"\t{serv}" + Color.END)
        return os.linesep.join(messages)

    def availX(self) -> str:
        """
        Display available services extend.
        """
        messages: List[str] = []
        messages.append(f"Available services:")
        for serv in self.services.values():
            messages.append(
                Color.BOLD
                + f"\t{serv.name}:{os.linesep}"
                + Color.END
                + f"\t{serv.props}"
                + os.linesep
            )
        return os.linesep.join(messages)

    def availXL(self) -> str:
        """
        Display available services extend with default values.
        """
        messages: List[str] = []
        messages.append(f"Available services:")
        for serv in self.services.values():
            messages.append(Color.BOLD + f"\t{serv.name}:" + Color.END)
            messages.append(
                "".join(f"\t{k}:\t{v}{os.linesep}" for k, v in vars(serv).items())
            )
        return os.linesep.join(messages)

    def terminate(self) -> str:
        """
        Exit taskmaster and all its programs.
        """
        messages: List[str] = []
        for serv in self.services.values():
            messages.append(serv.stop())
        return os.linesep.join(messages)

    def status(self, args: Optional[List[str]] = None) -> str:
        """
        Display the status of the mentionned service(s). All services if not specified
        """
        messages: List[str] = []
        if args is None or len(args) == 0 or (args[0] == "all" and len(args) == 1):
            for serv in self.services.values():
                messages.append(serv.status())
            return os.linesep.join(messages)
        for arg in args:
            if arg in self.services.keys():
                messages.append(self.services[arg].status())
            else:
                messages.append(f"Service not found: {arg}")
        return os.linesep.join(messages)

    def reload(self) -> str:
        """
        Reload the configuration file.
        Accept only the last defined service if the service is defined multiple times
        """
        logger.info("Reloading...")
        messages: List[str] = []
        try:
            new_conf = load_config(self.configPath)
            validateConfig(new_conf)
        except Exception as e:
            logger.warning(f"Failed to reload configuration: {e}")
            messages.append(f"Failed to reload configuration: {e}")
            return os.linesep.join(messages)

        if new_conf == self.fullconfig:
            logger.info("Configuration didn't change")
            messages.append("Configuration didn't change")
            return os.linesep.join(messages)

        # New services or known services
        i: int = 1
        for new_props in new_conf["services"]:
            name = new_props["name"]
            # Known
            if name in self.services.keys() and name not in [
                serv["name"] for serv in new_conf["services"][i:]
            ]:
                if new_props != self.services[name].props:
                    messages.append(f"{name}: process group updated -> will stop and start")
                    messages.append(self.services[name].reload(new_props))
                else:
                    messages.append(f"{name}: process group didn't change")
            # New
            elif name not in [serv["name"] for serv in new_conf["services"][i:]]:
                messages.append(f"{name}: process group added")
                self.services[name] = Service(name, new_props)
            i += 1

        # List of services to remove
        services_to_remove: List[str] = [
            service.name
            for service in self.services.values()
            if service.name
            not in [new_props["name"] for new_props in new_conf["services"]]
        ]
        # Stop and remove the service
        # TODO: test for removed process that didnt terminated on stop request
        for serv in services_to_remove:
            messages.append(f"{serv}: process group removed -> will stop processes")
            messages.append(self.services[serv].stop())
            self.services.pop(serv)
        self.fullconfig = new_conf
        return os.linesep.join(messages)

    def start(self, args: Optional[List[str]] = None) -> str:
        """
        Start mentionned services. All services if not specified
        """
        messages: List[str] = []
        if args is None or len(args) == 0 or (len(args) == 1 and args[0] == "all"):
            for serv in self.services.values():
                messages.append(serv.start())
            return os.linesep.join(messages)
        for arg in args:
            if arg in self.services.keys():
                messages.append(self.services[arg].start())
            else:
                logger.warning(f"Service not found: {arg}")
                messages.append(f"Service not found: {arg}")
        return os.linesep.join(messages)

    def stop(self, args: Optional[List[str]] = None) -> None:
        """
        Stop mentionned services. All services if not specified
        """
        messages: List[str] = []
        if args is None or len(args) == 0 or (args[0] == "all" and len(args) == 1):
            for serv in self.services.values():
                messages.append(serv.stop())
            return os.linesep.join(messages)
        for arg in args:
            if arg in self.services.keys():
                messages.append(self.services[arg].stop())
            else:
                logger.warning(f"Service not found: {arg}")
        return os.linesep.join(messages)

    def restart(self, args: Optional[List[str]] = None) -> None:
        """
        Restart mentionned services. All services if not specified
        """
        messages: List[str] = []
        if args is None or len(args) == 0 or (args[0] == "all" and len(args) == 1):
            for serv in self.services.values():
                messages.append(serv.kill())
            for serv in self.services.values():
                messages.append(serv.start())
            return os.linesep.join(messages)
        for arg in args:
            if arg in self.services.keys():
                messages.append(self.services[arg].kill())
            else:
                logger.warning(f"Service not found: {arg}")
                messages.append(f"Service not found: {arg}")
        for arg in args:
            if arg in self.services.keys():
                messages.append(self.services[arg].start())
        return os.linesep.join(messages)
