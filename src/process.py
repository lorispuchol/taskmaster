import subprocess
from enum import Enum


class State(Enum):
    """
    The different states of a process: see http://supervisord.org/subprocess.html#process-states
    """

    STOPPED = "STOPPED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    BACKOFF = "BACKOFF"
    STOPPING = "STOPPING"
    EXITED = "EXITED"
    FATAL = "FATAL"
    # UNKNOWN = "unknown"  # Not used in taskmaster due to the subject


# Inerit from subprocess.Popen
class Process(subprocess.Popen):
    def __init__(self, pid: int, name: str, state: State = State.STOPPED):
        self.pid: int = pid
        self.name: str = (
            name  ## <servicename_processnumber> (e.g. "myprogam" if one process, "myprogram_1" and myprogram_2 if 2 processes)
        )
        self.state: State = state

    def status(self) -> str:
        return f"Process {self.name} with PID {self.pid} is {self.state.value}"
    
    def stop(self) -> str:
        return f"Stopping {self.name}"
