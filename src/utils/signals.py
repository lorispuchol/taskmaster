import signal

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
    # 'STKFLT':   signal.SIGSTKFLT,   # for Linux, not MacOS
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
    # 'POLL':     signal.SIGPOLL,     # equivalent to SIGIO     # for Linux, not MacOS
    # 'PWR':      signal.SIGPWR,                                # for Linux, not MacOS
    'SYS':      signal.SIGSYS,      # equivalent to SIGUNUSED
    # 'UNUSED':   signal.SIGUNUSED, # equivalent to SIGSYS
    # 'INFO':     signal.SIGINFO,                                 # for MacOS, not Linux
    # 'WINCH':    signal.SIGWINCH,                                # for MacOS, not Linux
    # 'EMT':      signal.SIGEMT,                                  # for MacOS, not Linux
}