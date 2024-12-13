from enum import Enum
import signal
import subprocess
import cerberus

required_program_props = ["cmd"]

SIGNALS = {
    # Signal for x86/ARM https://man7.org/linux/man-pages/man7/signal.7.html
    # https://faculty.cs.niu.edu/~hutchins/csci480/signals.htm
    # listed here: '$ kill -l'
    # dict because use string for signal in config file
    'HUP':      signal.SIGHUP,
    'INT':      signal.SIGINT,
    'QUIT':     signal.SIGQUIT,
    'ILL':      signal.SIGILL,
    'TRAP':     signal.SIGTRAP,
    'IOT':      signal.SIGIOT ,     # equivalent to SIGABRT
    'ABRT':     signal.SIGABRT,     # equivalent to SIGIOT
    'BUS':      signal.SIGBUS,
    'FPE':      signal.SIGFPE,
    'KILL':     signal.SIGKILL,
    'USR1':     signal.SIGUSR1,
    'SEGV':     signal.SIGSEGV,
    'USR2':     signal.SIGUSR2,
    'PIPE':     signal.SIGPIPE,
    'ALRM':     signal.SIGALRM,
    'TERM':     signal.SIGTERM,
    'STKFLT':   signal.SIGSTKFLT,
    'CHLD':     signal.SIGCHLD,
    'CONT':     signal.SIGCONT,
    'STOP':     signal.SIGSTOP,
    'TSTP':     signal.SIGTSTP,
    'TTIN':     signal.SIGTTIN,
    'TTOU':     signal.SIGTTOU,
    'URG':      signal.SIGURG,
    'XCPU':     signal.SIGXCPU,
    'XFSZ':     signal.SIGXFSZ,
    'VTALRM':   signal.SIGVTALRM,
    'PROF':     signal.SIGPROF,
    'WINCH':    signal.SIGWINCH,
    'IO':       signal.SIGIO,       # equivalent to SIGPOLL
    'POLL':     signal.SIGPOLL,     # equivalent to SIGIO
    'PWR':      signal.SIGPWR,
    'SYS':      signal.SIGSYS,      # equivalent to SIGUNUSED
    # 'UNUSED':   signal.SIGUNUSED,   # equivalent to SIGSYS
}

class ServiceState(Enum):
    """
    Process State: see http://supervisord.org/subprocess.html#process-states
    """
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    BACKOFF = "backoff"
    STOPPING = "stopping"
    EXITED = "exited"
    FATAL = "fatal"
    # UNKNOWN = "unknown"  # Not used in taskmaster due to the subject

class AllowedAutoRestartValues(Enum):
    """Allowed value for 'autorestart' property"""
    NEVER = "never"
    ALWAYS = "always"
    UNEXPECTED = "unexpected"


class AllowedStopSignalsValues(Enum):
    """Allowed value for 'stopsignal' property"""
    TERM = "TERM"
    HUP = "HUP"
    INT = "INT"
    QUIT = "QUIT"
    KILL = "KILL"
    USR1 = "USR1"
    USR2 = "USR2"



schema = {
    "servicename": {
        "type": "dict",
        "schema": {
            "cmd": {
                "type": "string",
                "required": True,
                'empty': False,
            },
            "numprocs": {
                "type": "integer",
                "min": 1,
                "max": 32,
                "default": 1,
            },
            "autostart": {
                "type": "boolean",
                "default": True,
            },
            "starttime": {
                "type": "integer",
                "min": 0,
                "default": 1,
            },
            "startretries": {
                "type": "integer",
                "min": 1,
                "max": 10,
                "default": 3,
            },
            "autorestart": {
                "type": "string",
                "allowed": [v.value for v in AllowedAutoRestartValues],
                "default": AllowedAutoRestartValues.UNEXPECTED.value,
            },
            "exitcodes": {
                "type": "list",
                "schema": {
                    "type": "integer",
                    "min": 0,
                    "max": 255,
                },
                "default": [0], # success exit code
            },
            "stopsignal": {
                "type": "string",
                "allowed": [v.value for v in AllowedStopSignalsValues],
                "default": AllowedStopSignalsValues.TERM.value,
            },
            "stoptime": {
                "type": "integer",
                "min": 0,
                "default": 10,
            },
            "env": {
                "type": "dict",
            },
            "workingdir": {
                "type": "string",
            },
            "umask": {
                "type": "integer",
                "min": 0o0,
                "max": 0o777,
            },
            "stdout": {
                "type": "string",
            },
            "stderr": {
                "type": "string",
            },
            "user": {
                "type": "string",
            },
        },
    },
}


def is_valid_service(seviceName: str, serviceProps: dict) -> bool:
    """
    Check if the given service properties are valid.
    Valid means: serviceProps is a dict, serviceProps contains all required properties. Properties have the right type and valid values.

    Args:
        serviceProps (dict): The service properties to check.

    Returns:
        bool: True if the service properties are valid, False otherwise.
    """

class Service():
    def __init__(self, name: str, props: dict):
        self.name: str = name
        self.props: dict = props
        self.processes: list[Process] = []

    def updateProps(self, props: dict):
        self.props = props
        # TODO Update the process with the new properties


        # Props see http://supervisord.org/configuration.html#program-x-section-settings
        # cmd: str = command  # Required 
        # numprocs: int = numprocs
        # umask: int = umask
        # workingdir: str = workingdir
        # autostart: bool = autostart
        # autorestart: str = autorestart # authorized values LookForRestart enum
        # exitcodes: list[int] = exitcodes # list of exit code considered as normal exit >= 0 and <= 255 (see https://www.agileconnection.com/article/overview-linux-exit-codes and https://hpc-discourse.usc.edu/t/exit-codes-and-their-meanings/414)
        # startretries: int = startretries > 0
        # starttime: int = starttime
        # stopsignal: str = stopsignal # authorized values: SIGNALS dictionnary
        # stoptime: int = stoptime
        # stdout: str = stdout
        # stderr: str = stderr
        # env: dict[str, str] = env
        # user: str = user # user to run as (or uid): Bonus

class Process(subprocess.Popen):
    def __init__(self, pid: int, name: str, state: ServiceState):
        self.pid: int = pid
        self.name: str = name ## <servicename_processnumber> (e.g. "myprogam" if one process, "myprogram_1" and myprogram_2 if 2 processes) 
        self.state: ServiceState = state

    def __str__(self):
        return f"Process {self.name} with PID {self.pid} is {self.state.value}"
