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
