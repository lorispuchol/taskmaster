from enum import Enum
import signal
import subprocess
import json
from logger import logger
import os
from io import TextIOWrapper


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

class State(Enum):
    """
    The different states of a process: see http://supervisord.org/subprocess.html#process-states
    """
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    BACKOFF = "backoff"
    STOPPING = "stopping"
    EXITED = "exited"
    FATAL = "fatal"
    # UNKNOWN = "unknown"  # Not used in taskmaster due to the subject

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
    

class Service():
    def __init__(self, name: str, props: dict):
        self.name: str = name
        self.props: dict = props
        self.processes: list[Process] = []
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
        self.umask = props.get("umask", -1) # Must inherit from the master process by default
        self.stdout = props.get("stdout", "/dev/null")
        self.stderr = props.get("stderr", "/dev/null")
        # for bonus
        self.user = props.get("user", None) # Must inherit from the master process by default
        # self.start()


    def updateProps(self, props: dict):
        # TODO Update the process with the new properties
        self.props = props

    def start(self):
        try:
            with open(self.stdout, "w") as f:
                # print(self.stdout)
                
                result = subprocess.Popen([self.cmd,], stdin=subprocess.DEVNULL)
                # print(result.stdout.read())
        except Exception as e:
            logger.error(f"Error while opening {self.stdout}: {e}")
            

class Process(subprocess.Popen):
    def __init__(self, pid: int, name: str, state: State):
        self.pid: int = pid
        self.name: str = name ## <servicename_processnumber> (e.g. "myprogam" if one process, "myprogram_1" and myprogram_2 if 2 processes) 
        self.state: State = state

    def __str__(self):
        return f"Process {self.name} with PID {self.pid} is {self.state.value}"