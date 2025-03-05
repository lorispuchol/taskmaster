import os
from enum import Enum
from logger import logger
from typing import List, Dict
from process import Process, State


class AutoRestart(Enum):
    """Allowed value for 'autorestart' property"""
    NEVER = "never"
    ALWAYS = "always"
    UNEXPECTED = "unexpected"


class StopSignals(Enum):
    """Allowed value for 'stopsignal' property
    Defined in supervisor documentation:"""
    TERM = "SIGTERM"
    HUP = "SIGHUP"
    INT = "SIGINT"
    QUIT = "SIGQUIT"
    KILL = "SIGKILL"
    USR1 = "SIGUSR1"
    USR2 = "SIGUSR2"


class ServiceState(Enum):
    """State of the the service after a reload query"""
    UPDATING = "UPDATING"
    RESTARTING = "RESTARTING"
    NOTHING = "NOTHING"
    REMOVING = "REMOVING"


class Service:
    def __init__(self, name: str, props: Dict):
        """
        Initialize a service object with its properties and processes.
        """
        self.name: str = name
        self.props: Dict = props
        self.processes: List[Process] = []
        self.setProps(props)
        self.initProcesses()
        self.state: ServiceState = ServiceState.NOTHING

    def setProps(self, props: Dict):
        """
        Sets the attributes from the configuration
        Set default values if ommit in the configuration
        """
        self.name: str = props.get("name")
        self.cmd: str = props.get("cmd")
        self.numprocs: int = props.get("numprocs", 1)  # No need restart if changed
        self.autostart: bool = props.get("autostart", True)
        self.starttime: int = props.get("starttime", 1)
        self.startretries: int = props.get("startretries", 3)
        self.autorestart: str = props.get("autorestart", AutoRestart.UNEXPECTED.value)
        self.exitcodes: List[int] = props.get(
            "exitcodes", [0]
        )  # No need restart if changed
        self.stopsignal: str = props.get("stopsignal", StopSignals.TERM.value)
        self.stoptime: int = props.get("stoptime", 10)
        self.env: Dict = props.get("env", {})
        self.workingdir: str = props.get("workingdir", "/tmp")
        self.umask: int = props.get("umask", -1)  # Default: inherit from master
        self.stdout: str = props.get("stdout", "/dev/null")
        self.stderr: str = props.get("stderr", "/dev/null")
        # for bonus

        self.user: str = props.get("user", None)  # Default: inherit from master

        self.props = props

    def initProcesses(self) -> None:
        """
        Initialize the processes of the service.
        """
        for i in range(self.numprocs):
            self.processes.append(
                Process(
                    name=(
                        f"{self.name}:{self.name}_{i+1}"
                        if self.numprocs > 1
                        else self.name
                    ),
                    props=self.__dict__,
                )
            )

    def status(self) -> str:
        """
        Return the status of the service.
        """
        messages: List[str] = []
        for process in self.processes:
            messages.append(process.status())
        return os.linesep.join(messages)

    def reload(self, new_props) -> str:
        """
        Reload the service. Do nothing if its configuration didn't change.
        """
        # No restart because stop process needs the old properties
        messages: List[str] = []
        if new_props != self.props:
            messages.append(self.kill())
            self.setProps(new_props)
            if self.autostart == True:
                messages.append(self.start())
        return os.linesep.join(messages)

    def start(self) -> str:
        """
        Start the service.
        """
        messages: List[str] = []
        for process in self.processes:
            messages.append(process.start())
        return os.linesep.join(messages)

    def stop(self) -> str:
        """
        Stop the service.
        """
        messages: List[str] = []
        for process in self.processes:
            messages.append(process.stop())
        return os.linesep.join(messages)

    def kill(self) -> str:
        """
        Terminate the service (with sigkill).
        """
        messages: List[str] = []
        for process in self.processes:
            messages.append(process.kill())
        return os.linesep.join(messages)