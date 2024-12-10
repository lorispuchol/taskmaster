from enum import Enum

required_program_props = ["cmd"]


# Process State: see http://supervisord.org/subprocess.html#process-states
class ProcessState(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    BACKOFF = "backoff"
    STOPPING = "stopping"
    EXITED = "exited"
    FATAL = "fatal"

class Program:
    def __init__(self, name: str, props: dict, pid: int = None):
        self.name: str = name
        self.props: dict = props

        if not self.props:
            raise Exception("No properties found for program")
        if not all(prop in self.props for prop in required_program_props):
            raise Exception(f"Missing required properties for {self.name} program: {required_program_props} required")
        

        # Props see http://supervisord.org/configuration.html#program-x-section-settings
        # cmd: str = command  # Required 
        # numprocs: int = numprocs
        # umask: int = umask
        # workingdir: str = workingdir
        # autostart: bool = autostart
        # autorestart: str = autorestart # authorized values {never, always, unexpected}
        # exitcodes: list[int] = exitcodes # list of exit code considered as normal exit
        # startretries: int = startretries
        # starttime: int = starttime
        # stopsignal: str = stopsignal # authorized values {HUP INT QUIT ILL TRAP IOT(SIGIOT=SIGABRT) BUS FPE KILL USR1 SEGV USR2 PIPE ALRM TERM STKFLT CHLD CONT STOP TSTP TTIN TTOU URG XCPU XFSZ VTALRM PROF WINCH POLL(SIGPOLL=SIGIO) PWR SYS(SIGSYS=SIGUNUSED)} nb=31 see https://faculty.cs.niu.edu/~hutchins/csci480/signals.htm (No SIGCLD ?)
        # stoptime: int = stoptime
        # stdout: str = stdout
        # stderr: str = stderr
        # env: dict[str, str] = env


        
