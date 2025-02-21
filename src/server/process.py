import datetime, subprocess
from enum import Enum
from logger import logger
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
class Process():
    def __init__(self, name: str, props: dict):
        self.name: str = name
        self.state: State = State.STOPPED
        self.startdate: datetime.datetime | None = None
        self.stopdate: datetime.datetime | None = None
        self.exitdate: datetime.datetime | None = None
        self.pid: int = 0
        self.props: dict = props
        self.proc: subprocess.Popen | None = None
        self.graceful_stop: bool = False

    def status(self) -> str:
        # ls                               BACKOFF   Exited too quickly (process log may have details)
        # ls                               EXITED    Jan 31 05:26 AM
        # ping:ping_0                      STOPPED   Jan 31 05:51 AM
        # ping:ping_1                      RUNNING   pid 62330, uptime 0:31:00
        # ping:ping_2                      RUNNING   pid 62331, uptime 0:31:00
        # sleep                            RUNNING   pid 71413, uptime 0:00:01
        #
        # sleep                            STARTING
        # ls                               FATAL     Exited too quickly (process log may have details)

        # print(m)
        # for serv in self.services.values():
        #     print(Color.BOLD + f"\t{serv.name}:".ljust(m + 1), end=Color.END + "\n")
        if (self.state == State.STARTING or self.state == State.STOPPING):
            return f"{self.name}" + (43 - 2 * len(self.name)) * " " + f"{self.state}"
        elif (self.state == State.RUNNING):
            return (
                f"{self.name}"
                + (43 - 2 * len(self.name)) * " "
                + f"{self.state}\tpid {self.pid},\t uptime {datetime.datetime.now() - self.startdate}"
            )
        elif self.state == State.STOPPED:
            return f"{self.name}" + (43 - len(self.name)) * " " + f"{self.state}\t{self.stopdate}"
        elif self.state == State.EXITED:
            return f"{self.name}" + (43 - len(self.name)) * " " + f"{self.state}\t{self.exitdate}"
        elif self.state == State.FATAL or self.state == State.BACKOFF:
            return f"{self.name}" + (43 - len(self.name)) * " " + f"{self.state} Le message derror"

    def start(self) -> str:
        try:
            with open(self.props["stdout"], "w") as f_out, open(self.props["stderr"], "w") as f_err:
                self.proc = subprocess.Popen(
                    self.props["cmd"].split(),
                    stdout=f_out,
                    stderr=f_err,
                    stdin=subprocess.DEVNULL,
                    text=True,
                )
                # print(self.name, self.proc.pid)
                # while proc.poll() is None:
                #     pass
        except FileNotFoundError as e:
            logger.error(f"{e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        return f"Starting {self.name}"
        # ping:ping_0: started
        # ping:ping_0: ERROR (already started)
        # supervisor> start ls
        # ls: ERROR (spawn error)


    def stop(self) -> str:
        if self.proc is not None:
            self.proc.terminate()
            self.proc.wait()
            self.stopdate = datetime.datetime.now()
            self.state = State.STOPPED
            self.graceful_stop = True
            return f"Stopping {self.name}"
        # return f"Stopping {self.name}"
        # ping:ping_0: stopped
        # ping:ping_0: ERROR (not running)
        return f"{self.name}: ERROR (not running)"

    @property
    def getState(self) -> State:
        return self.state