class Program:
    def __init__(
        self,
        name,
        command,
        numprocs,
        umask,
        workingdir,
        autostart,
        autorestart,
        exitcodes,
        startretries,
        starttime,
        stopsignal,
        stoptime,
        stdout,
        stderr,
    ):
        self.name: str = name  # Parent object in file: 1 minumum required
        self.cmd: str = command  # Required
        self.numprocs: int = numprocs
        self.umask: int = umask
        self.workingdir: str = workingdir
        self.autostart: bool = autostart
        self.autorestart: str = autorestart
        self.exitcodes: list[int] = exitcodes
        self.startretries: int = startretries
        self.starttime: int = starttime
        self.stopsignal: str = stopsignal
        self.stoptime: int = stoptime
        self.stdout: str = stdout
        self.stderr: str = stderr

required_props = ["cmd"]

class OneProgram:
    def __init__(self, name: str, props: dict):
        self.name: str = name
        self.props: dict = props

        if not self.props:
            raise Exception("No properties found for program")
        
        # cmd: str = command  # Required
        # numprocs: int = numprocs
        # umask: int = umask
        # workingdir: str = workingdir
        # autostart: bool = autostart
        # autorestart: str = autorestart # authorized values {never, always, unexpected}
        # exitcodes: list[int] = exitcodes
        # startretries: int = startretries
        # starttime: int = starttime
        # stopsignal: str = stopsignal # authorized values {HUP INT QUIT ILL TRAP IOT(SIGIOT=SIGABRT) BUS FPE KILL USR1 SEGV USR2 PIPE ALRM TERM STKFLT CHLD CONT STOP TSTP TTIN TTOU URG XCPU XFSZ VTALRM PROF WINCH POLL(SIGPOLL=SIGIO) PWR SYS(SIGSYS=SIGUNUSED)} nb=31 see https://faculty.cs.niu.edu/~hutchins/csci480/signals.htm (No SIGCLD ?)
        # stoptime: int = stoptime
        # stdout: str = stdout
        # stderr: str = stderr
