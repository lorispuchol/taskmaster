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
        self.setProps(props)

    def setProps(self, props: Dict):
        """
        Sets the attributes to those of the configuration
        Or the default values if not present in the configuration
        """
        self.name: str = props.get("name")
        self.cmd: str = props.get("cmd")
        self.numprocs: int = props.get("numprocs", 1)  # No need restart if changed
        self.autostart: bool = props.get("autostart", True)
        self.starttime: int = props.get("starttime", 1)
        self.startretries: int = props.get("startretries", 3)
        self.autorestart: str = props.get("autorestart", AutoRestart.UNEXPECTED.value)
        self.exitcodes: List[int] = props.get("exitcodes", [0]) # No need restart if changed
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
        # ls                               BACKOFF   Exited too quickly (process log may have details)
        # ls                               EXITED    Jan 31 05:26 AM
        # ping:ping_0                      STOPPED   Jan 31 05:51 AM
        # ping:ping_1                      RUNNING   pid 62330, uptime 0:31:00
        # ping:ping_2                      RUNNING   pid 62331, uptime 0:31:00
        # sleep                            RUNNING   pid 71413, uptime 0:00:01
        # 
        # sleep                            STARTING
        # ls                               FATAL     Exited too quickly (process log may have details)

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
                    # start_new_session=True,  # Create a new process group to avoid zombie processes
                )
        except FileNotFoundError as e:
            logger.error(f"{e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        return message

    # ping:ping_0: started
    # ping:ping_0: ERROR (already started)
    # supervisor> start ls
        # ls: ERROR (spawn error)

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