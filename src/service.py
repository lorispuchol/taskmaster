from enum import Enum
import subprocess, os
from utils.logger import logger
from typing import List, Dict
from process import Process, State


class AutoRestart(Enum):
    """Allowed value for 'autorestart' property"""

    NEVER = "never"
    ALWAYS = "always"
    UNEXPECTED = "unexpected"


class StopSignals(Enum):
    """Allowed value for 'stopsignal' property"""

    TERM = "TERM"
    HUP = "HUP"
    INT = "INT"
    QUIT = "QUIT"
    KILL = "KILL"
    USR1 = "USR1"
    USR2 = "USR2"


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
                    name=f"{self.name}_{i+1}" if self.numprocs > 1 else self.name,
                    props=self.__dict__
                )
            )    

    def status(self) -> List[str]:
        """
        Return the status of the service.
        """
        message: List[str] = []
        for process in self.processes:
            message.append(process.status())
        return message

    def reload(self, new_props) -> List[str]:
        """
        Reload the service. Do nothing if its configuration didn't change.
        """
        # No restart because stop process needs the old properties
        if new_props != self.props:
            stop_msg = self.stop()
            self.setProps(new_props)
            if self.autostart == True:
                return stop_msg + self.start()

    def start(self) -> str:

        messages: List[str] = []

        logger.info(f"Starting {self.name}")
        for process in self.processes:  
            messages.append(process.start())
        return "\n".join(messages)

    def stop(self) -> List[str]:
        """
        Stop the service.
        """
        message: List[str] = []
        for process in self.processes:
            message.append(process.stop())
        return message
