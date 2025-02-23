import datetime, subprocess, signal, time
from enum import Enum
from logger import logger


def getLogfile(path: str):
    try:
        with open(path, "w") as fd:
            return fd
    except Exception as e:
        logger.error(
            f"Failed to access log file <{path}>: {e}, using /dev/null instead"
        )
        return subprocess.DEVNULL


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
class Process:
    def __init__(self, name: str, props: dict):
        self.name: str = name
        self.state: State = State.STOPPED
        self.changedate: datetime.datetime | None = None
        self.props: dict = props
        self.proc: subprocess.Popen | None = None
        self.graceful_stop: bool = True
        self.current_retry: int = 1
        self.error_message: str = ""
        if props["autostart"]:
            self.start()

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

        message: str = ""
        if self.state == State.STARTING or self.state == State.STOPPING:
            message = (
                f"{self.name}" + (43 - len(self.name)) * " " + f"{self.state.value}   "
            )
        elif self.state == State.RUNNING:
            message = (
                f"{self.name}"
                + (43 - len(self.name)) * " "
                + f"{self.state.value}   pid {self.proc.pid},\t uptime {datetime.datetime.now() - self.changedate}"
            )
        elif self.state == State.STOPPED:
            message = (
                f"{self.name}" + (43 - len(self.name)) * " " + f"{self.state.value}   "
            )
            if self.changedate is not None:
                message += f"{self.changedate}"
        elif self.state == State.EXITED:
            message = (
                f"{self.name}" + (43 - len(self.name)) * " " + f"{self.state.value}    "
            )
            if self.changedate is not None:
                message += f"\t{self.changedate}"
        elif self.state == State.FATAL:
            message = (
                f"{self.name}"
                + (43 - len(self.name)) * " "
                + f"{self.state.value}     {self.error_message}"
            )
        elif self.state == State.BACKOFF:
            message = (
                f"{self.name}"
                + (43 - len(self.name)) * " "
                + f"{self.state.value}   {self.error_message}"
            )
        return message

    def start(self) -> str:
        if self.state == State.RUNNING or self.state == State.STARTING:
            return f"{self.name}: ERROR (already started)"
        if self.state == State.BACKOFF:
            self.state = State.STARTING
        logger.info(f"Start request received for: {self.name}")
        try:
            with open(self.props["stdout"], "w") as f_out, open(
                self.props["stderr"], "w"
            ) as f_err:
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
            self.graceful_stop = False
        except Exception as e:
            logger.error(f"Unexpected Error trying to start {self.name}: {e}")
            self.state = State.FATAL
            self.error_message = str(e)
            self.changedate = datetime.datetime.now()
            return f"{self.name}: ERROR (spawn error)"

        self.state = State.STARTING
        self.changedate = datetime.datetime.now()
        return f"{self.name}: starting"
        # ping:ping_0: started
        # ping:ping_0: ERROR (already started)
        # supervisor> start ls
        # ls: ERROR (spawn error)

    def stop(self) -> str:
        if self.proc is not None and (
            self.state == State.RUNNING
            or self.state == State.STARTING
            or self.state == State.BACKOFF
        ):
            logger.info(f"Stop request received for: {self.name}")
            self.graceful_stop = True
            self.state = State.STOPPING
            self.changedate = datetime.datetime.now()
            self.proc.send_signal(signal.Signals[self.props["stopsignal"]].value)
            self.proc.poll()
            if self.props["stoptime"] <= 0:
                self.proc.kill()
                self.proc.wait()
                self.state = State.STOPPED
                self.changedate = datetime.datetime.now()
                logger.info(f"{self.name}: {self.proc.pid} has been killed")
                self.proc = None
                return f"{self.name}: stopped (killed)"
            elif self.proc.returncode is not None:
                self.state = State.STOPPED
                self.changedate = datetime.datetime.now()
                logger.info(f"{self.name}: {self.proc.pid} has been stopped")
                self.proc = None
                return f"{self.name}: stopped"
            return f"{self.name}: stopping"
        return f"{self.name}: ERROR (not running)"

    @property
    def getState(self) -> State:
        return self.state
