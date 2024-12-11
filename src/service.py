from enum import Enum
import signal
import subprocess

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
    'UNUSED':   signal.SIGUNUSED,   # equivalent to SIGSYS
}

class State(Enum):
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

class LookForRestart(Enum):
    NEVER = "never"
    ALWAYS = "always"
    UNEXPECTED = "unexpected"

class Service():
    def __init__(self, name: str, props: dict, pid: int = None):
        self.name: str = name
        self.props: dict = props

        if not self.props:
            raise Exception("No properties found for program")
        if not all(prop in self.props for prop in required_program_props):
            raise Exception(f"Missing required properties for {self.name} program: {required_program_props} required")
        
    def updateProps(self, props: dict):
        self.props = props


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
    def __init__(self, pid: int, name: str, state: State):
        self.pid: int = pid
        self.name: str = name ## name of the Service_<process-number>
        self.state: State = state

    def __str__(self):
        return f"Process {self.name} with PID {self.pid} is {self.state.value}"
