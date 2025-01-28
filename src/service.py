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
        # print(json.dumps(props, indent=4))

        # All unrequired properties are set to default values if not present in the configuration file
        self.name = props.get("name")
        self.cmd = props.get("cmd")
        self.numprocs = props.get("numprocs", 1)
        self.autostart = props.get("autostart", True)
        self.starttime = props.get("starttime", 1)
        self.startretries = props.get("startretries", 3)
        self.autorestart = props.get("autorestart", AutoRestart.UNEXPECTED.value)
        self.exitcodes = props.get("exitcodes", [0])
        self.stopsignal = props.get("stopsignal", StopSignals.TERM.value)
        self.stoptime = props.get("stoptime", 10)
        self.env = props.get("env", {})
        self.workingdir = props.get("workingdir", "/tmp")
        self.umask = props.get(
            "umask", -1
        )  # Must inherit from the master process by default
        self.stdout = props.get("stdout", "/dev/null")
        self.stderr = props.get("stderr", "/dev/null")

        # for bonus
        self.user = props.get(
            "user", None
        )  # Must inherit from the master process by default

    def updateProps(self, props: Dict):
        # TODO Update the process with the new properties
        self.props = props

    def start(self):

        logger.info(f"Starting service: {self.name}")

        try:
            with open(self.stdout, "w") as f:
                # print(self.stdout)

                result = subprocess.Popen(
                    [
                        self.cmd,
                    ],
                    stdin=subprocess.DEVNULL,
                )
                # print(result.stdout.read())
                # result.kill()
        except Exception as e:
            logger.error(f"Error while opening {self.stdout}: {e}")
