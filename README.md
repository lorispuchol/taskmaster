# taskmaster

TODO:

- rewrite process.start() method
- add tests
- umask
- workingdir
- env
- user (run with sudo)
- unwrite unused function in Process and Service classes
- plusieurs processus qui log dans le meme fichier
- test shutdown    

NOTES:

stop request for: [X] == OK  
    RUNNING []  
    FATAL []  
    STOPPED []  
    STOPPING []  
    EXITED []  
    BACKOFF []  
    STARTING []  

start request for: [X] == OK   
    RUNNING []  
    FATAL []  
    STOPPED []  
    STOPPING []  
    EXITED []  
    BACKOFF [] if start request on BACKOFF process. It will ingore the request (doesn't try to start again and doesn't reset the number of retries)  
    STARTING []  

## Service properties documentation

See supervisord http://supervisord.org/configuration.html#program-x-section-settings

### cmd

The command to run with arguments. (path absolute or relative)

- Type: str
- Required

### numprocs

The number of processes to start. If > 1, the `process_name` will be suffixed with the process number.

- Type: int
- Default: 1
- Constraints: 1 <= numprocs <= 32

### autostart

If true, the process will start automatically when the taskmaster starts.

- Type: bool
- Default: True

### starttime

The total number of seconds which the program needs to stay running after a startup to consider the start successful (moving the process from the `STARTING` state to the `RUNNING` state)

- Type: int
- Default: 1
- Constraints: 0 <= starttime

### startretries

The number of serial failure attempts that taskmaster will allow when attempting to start the program before giving up and putting the process into an `FATAL` state. (wait 1 second more between each attempt)

> After each failed restart, process will be put in `BACKOFF` state and each retry attempt will take increasingly more time.

- Type: int
- Default: 3
- Constraints: 0 < startretries <= 10

### autorestart

Specifies if taskmaster should automatically restart a process if it exits when it is in the `RUNNING` state. If unexpected, the process will be restarted when the program exits with an exit code that is not one of the `exitcodes`

- Type: str
- Default: "unexpected"
- Constraints: "unexpected", "always", "never"

### exitcodes

The list of integer exit codes that indicate a normal exit. Used in conjunction with `autorestart`

- Type: [int] (list of integers)
- Default: [0] (list with one element)
- Constraints: 0 <= exitcodes[i] <= 255

> Exit code status = 128 + signal number (if killed by a signal)  
> `echo $?`
>
> See:  
> https://man7.org/linux/man-pages/man7/signal.7.html  
> https://faculty.cs.niu.edu/~hutchins/csci480/signals.htm  
> https://www.agileconnection.com/article/overview-linux-exit-codes  
> https://hpc-discourse.usc.edu/t/exit-codes-and-their-meanings/414
> https://www.computerhope.com/unix/signals.htm
> https://stackoverflow.com/questions/1101957/are-there-any-standard-exit-status-codes-in-linux/1535733#1535733
> https://tldp.org/LDP/abs/html/exitcodes.html


### stopsignal
The signal used to kill the program when a stop is requested (i.e. exit gracefully)

- Type: str
- Default: "TERM"
- Constraints: "TERM", "HUP", "INT", "QUIT", "KILL", "USR1", "USR2"

### stoptime
The number of seconds to wait for the OS to return a SIGCHLD to taskmaster after the program has been sent a stopsignal. If this number of seconds elapses before taskmaster receives a SIGCHLD from the process, taskmaster will attempt to kill it with a final `SIGKILL`.

- Type: int
- Default: 10
- Constraints: 0 < stoptime

### env
A list of key/value pairs  that will be placed in the child process' environment.

- Type: {str: str} (dict)
- Default: None (No extra environment)

### workingdir
A file path representing a directory to which taskmaster should temporarily chdir before exec’ing the child.

- Type: str
- Default: None (Do not change working directory)

### umask
An octal number (e.g. 002, 022) representing the umask of the process.

- Type: int
- Default: None (No special umask, inherit supervisor’s) (-1 for `subprocess()` call. Maybe prefix with `0o` or `0` for octal)

### stdout
Put process stdout output in the specified file

- Type: str
- Default: None (Do not redirect stdout) (`/dev/null` for `subprocess()` call) (`subprocess.DEVNULL`)

### stderr
Put process stderr output in the specified file

- Type: str
- Default: None (Do not redirect stdout) (`/dev/null` for `subprocess()` call) (`subprocess.DEVNULL`)

### user
Instruct taskmaster to use this UNIX user account as the account which runs the program. The user can only be switched if taskmaster is run as the root user. If taskmaster can’t switch to the specified user, the program will not be started.

- Bonus
- Type: str
- Default: None (Do not switch user)

## Useful commands

### setup venv

```bash
source setup-venv.sh
```

### run taskmaster

```bash
python3 taskmaster.py <config.yml> -l LEVEL
```
> LEVEL = DEBUG, INFO, WARNING, ERROR, CRITICAL  
> INFO by default if not specified

### socket

```bash
sudo lsof -i :<port>
```

```bash
sudo ss -tulnp | grep <port>
```

```bash
sudo netstat -an | grep <port>
```

### processes

```bash
top -p `pgrep -d "," <program-name>`
```

```bash
top -U <user>
```

see this [link](https://phoenixnap.com/kb/top-command-in-linux) for top details

```bash
ps -ef | grep [<process> | <user>]
```

```bash
ps -u | grep <user>
```

```bash
ps aux | grep <process>
```

```bash
ps aux | grep <process> | awk '{print $2}' | xargs kill -9
```

```bash
kill -9 <pid>
# kill all processes you can kill
```

```bash
kill -HUP <pid>
```

### signals

```bash
kill -l
```

```bash
kill -l | tr ' ' '\n' | while read sig; do man 3 signal | grep -A1 "$sig " | head -n2; done
```
