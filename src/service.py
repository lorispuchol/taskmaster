from enum import Enum
import subprocess
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
        self.state: State = State.STOPPED

        # All unrequired properties are set to default values if not present in the configuration file
        self.name: str = props.get("name")
        self.cmd: str = props.get("cmd")
        self.numprocs: int = props.get("numprocs", 1)
        self.autostart: bool = props.get("autostart", True)
        self.starttime: int = props.get("starttime", 1)
        self.startretries: int = props.get("startretries", 3)
        self.autorestart: str = props.get("autorestart", AutoRestart.UNEXPECTED.value)
        self.exitcodes: List[int] = props.get("exitcodes", [0])
        self.stopsignal: str = props.get("stopsignal", StopSignals.TERM.value)
        self.stoptime: int = props.get("stoptime", 10)
        self.env: Dict = props.get("env", {})
        self.workingdir: str = props.get("workingdir", "/tmp")
        self.umask: int = props.get(
            "umask", -1
        )  # Must inherit from the master process by default
        self.stdout: str = props.get("stdout", "/dev/null")
        self.stderr: str = props.get("stderr", "/dev/null")

        # for bonus
        self.user: str = props.get(
            "user", None
        )  # Must inherit from the master process by default

    def updateProps(self, props: Dict):
        # TODO Update the process with the new properties
        self.props = props

    def status(self) -> List[str]:
        """
        Return the status of the service.
        """
        message: List[str] = []
        # for process in self.processes:
        #     message.append(process.status())
        message.append(f"Process {self.name} is {self.state.value}")
        
        return message
        # for process in self.processes:
        #     return process.status()
        # TODO Return the status of the service

    
    def reload(self, new_props) -> List[str]:
        """
        Reload the service. Do nothing if its configuration didn't change.
        """
        if new_props != self.props:
            self.updateProps(new_props)
            return self.restart()

    
    def start(self) -> List[str]:

        logger.info(f"Starting {self.name}")
        message: List[str] = []
        # for process in self.processes:
        #     message.append(process.start())
        message.append(f"Starting {self.name}")

        try:
            with open(self.stdout, "w") as f_out, open(self.stderr, "w") as f_err:
                proc = subprocess.Popen(
                    self.cmd.split(),
                    stdout=f_out,
                    stderr=f_err, 
                    stdin=subprocess.DEVNULL,
                    text=True,
                    start_new_session=True, # Create a new process group to avoid zombie processes 
                )
        except FileNotFoundError as e:
            logger.error(f"{e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        return message
    
    # ping:ping_0: started
    # ping:ping_0: ERROR (already started)
        

    def stop(self) -> List[str]:
        """
        Stop the service.
        """
        message: List[str] = []
        # for process in self.processes:
        #     message.append(process.stop())
        message.append(f"Stopping {self.name}")
        return message
        # TODO Stop the service
        # ping:ping_0: stopped
        # ping:ping_0: ERROR (not running)


    def restart(self) -> List[str]:
        """
        Restart the service.
        """
        return self.stop() + self.start()