import datetime, subprocess, signal
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
        message: str = ""
        if self.state == State.STARTING or self.state == State.STOPPING:
            message = (
                f"{self.name}" + (43 - len(self.name)) * " " + f"{self.state.value}   "
            )
        elif self.state == State.RUNNING:
            message = (
                f"{self.name}"
                + (43 - len(self.name)) * " "
                + f"{self.state.value}   pid {self.proc.pid}, uptime {datetime.datetime.now() - self.changedate}"
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
                message += f"{self.changedate}"
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
        logger.info(f"Start request for: {self.name}")
        if (
            self.state == State.RUNNING
            or self.state == State.STARTING
            or self.state == State.STOPPING
        ):
            logger.warning(f"{self.name}: ERROR (already started)")
            return f"{self.name}: ERROR (already started)"
        if self.state == State.BACKOFF:
            self.state = (
                State.STARTING
            )  # To avoid a start by monitoring on backoff state which would cause 2 differents starts
        try:
            with open(self.props["stdout"], "a") as f_out, open(
                self.props["stderr"], "a"
            ) as f_err:
                self.proc = subprocess.Popen(
                    self.props["cmd"].split(),
                    stdout=f_out,
                    stderr=f_err,
                    stdin=subprocess.DEVNULL,
                    text=True,
                    umask=self.props["umask"],
                    user=self.props["user"],
                    cwd=self.props["workingdir"],
                    env=self.props["env"],
                )
            self.graceful_stop = False
        except Exception as e:
            logger.critical(
                f"Unexpected Error encountered while trying to start {self.name}: {e}"
            )
            self.state = State.FATAL
            self.error_message = str(e)
            self.changedate = datetime.datetime.now()
            self.proc = None
            return f"{self.name}: ERROR (spawn error)"

        self.state = State.STARTING
        self.changedate = datetime.datetime.now()
        logger.info(f"Starting {self.name}")
        return f"{self.name}: starting"

    def stop(self) -> str:
        logger.info(f"Stop request for: {self.name}")
        self.current_retry = 1
        if self.proc is None and self.state == State.BACKOFF:
            self.state = State.STOPPED
            self.graceful_stop = True
            self.changedate = datetime.datetime.now()
            logger.info(f"{self.name}: stopped")
            self.proc = None
            return f"{self.name}: stopped"
        if self.proc is not None and (
            self.state == State.RUNNING
            or self.state == State.STARTING
            or self.state == State.BACKOFF
        ):
            self.graceful_stop = True
            self.state = State.STOPPING
            self.changedate = datetime.datetime.now()
            self.proc.send_signal(signal.Signals[self.props["stopsignal"]].value)
            self.proc.poll()
            if self.props["stoptime"] <= 0:
                return self.kill()
            elif self.proc.returncode is not None:
                self.state = State.STOPPED
                self.changedate = datetime.datetime.now()
                logger.info(f"{self.name}: {self.proc.pid} has been stopped")
                self.proc = None
                logger.info(f"Stopping {self.name}")
                return f"{self.name}: stopped"
            logger.info(f"Stopping {self.name}")
            return f"{self.name}: stopping"
        logger.warning(f"{self.name}: ERROR (not running)")
        return f"{self.name}: ERROR (not running)"

    def kill(self) -> str:
        self.current_retry = 1
        if (
            self.proc is None
            or self.state == State.STOPPED
            or self.state == State.EXITED
            or self.state == State.FATAL
        ):
            logger.error(f"Try to kill {self.name} but not running")
            return f"{self.name}: ERROR (not running)"
        self.proc.kill()
        self.proc.wait()
        self.state = State.STOPPED
        self.changedate = datetime.datetime.now()
        logger.info(f"{self.name}: {self.proc.pid} has been killed")
        self.proc = None
        return f"{self.name}: stopped (killed)"
