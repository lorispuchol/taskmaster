import socket, selectors, signal, sys, argparse
from logger import logger
from masterctl import MasterCtl
from config import load_config, validateConfig
from typing import List, Tuple

####################
# Global variables #
####################

master: MasterCtl = MasterCtl()
sel = selectors.DefaultSelector()
shutdown_flag = False


###########
# Signals #
###########


def signal_handler(sig, frame) -> None:
    """Handle signals (TERM, INT, QUIT, HUP).
    Calls the exit method of masterctl for TERM, INT, QUIT then exit with 128 + signumber.
    Reload the configuration file for HUP
    """
    # 'global' refers to the existing global variable (create it if not exist)
    global master
    global shutdown_flag

    logger.warning(
        f"Taskmaster (pid={master.pid}) received {signal.Signals(sig).name}({sig})"
    )
    if sig == signal.SIGHUP:
        master.reload()
    else:
        shutdown_flag = True
        sel.close()
        master.terminate()
        sys.exit(128 + sig)


def init_signal_handling() -> None:
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # TODO: Add signals is necessary ? (SIGTERM, SIGKILL, SIGUSR1, SIGUSR2 ?)


def process_monitoring():
    for service in master.services.values():
        for process in service.processes:
            if process.proc is not None and process.proc.poll() is not None:
                if service.autorestart and process.graceful_stopped == False:
                    logger.warning(
                        f"{process.name}: {process.proc.pid} exited. Restarting..."
                    )
                    try:
                        process.start()
                    except Exception as e:
                        print(f"Error restarting process: {e}")
                        # managed_processes.remove(entry)
                        continue
                    # entry["proc"] = new_proc
                # else:
                # managed_processes.remove(entry)
                # print(f"Removed exited process {proc.pid}")


####################
#   Server loop    #
####################


def select_action(cmd: str, args: List[str]) -> str:
    global shutdown_flag
    if cmd == "shutdown":
        # just like SIGTERM handling
        shutdown_flag = True
        sel.close()
        master.terminate()
        sys.exit(0)
    if cmd == "start":
        return master.start(args)
    if cmd == "stop":
        return master.stop(args)
    if cmd == "restart":
        return master.restart(args)
    if cmd == "status":
        return master.status(args)
    if cmd == "avail":
        return master.avail()
    if cmd == "availx":
        return master.availX()
    if cmd == "availxl":
        return master.availXL()
    if cmd == "reload":
        return master.reload()
    return f"Unknown command: {cmd}"
    


def accept_connection(sock):
    conn, addr = sock.accept()
    logger.info(f"Accept connection from {addr}")
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, data=handle_client)


def handle_client(conn):
    addr = conn.getpeername()
    try:
        data = conn.recv(4096)
        if data:
            message = data.decode().strip()
            logger.info(f"Received from {addr}: {message}")
            response = select_action(message.split()[0], message.split()[1:])
            conn.sendall(response.encode())
        else:
            logger.info(f"Connection closed by {addr}")
            sel.unregister(conn)
            conn.close()
    except ConnectionResetError:
        logger.warning(f"Connection reset by {addr}")
        sel.unregister(conn)
        conn.close()
    except Exception as e:
        logger.error(f"Error with {addr}: {e}")
        sel.unregister(conn)
        conn.close()


def run_server(host="0.0.0.0", port=65432):

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_sock.bind((host, port))
        server_sock.listen()
        server_sock.setblocking(False)
        sel.register(server_sock, selectors.EVENT_READ, data=accept_connection)
        logger.info(f"Server listening on {host}:{port}")

        while not shutdown_flag:
            print("ici") #
            events = sel.select(timeout=1)
            for key, mask in events:
                callback = key.data
                callback(key.fileobj)
            if not events:
                process_monitoring()
                pass

    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        logger.info("Cleaning up server...")
        server_sock.close()
        sel.close()
        logger.info("Taskmaster exited")


###########################
# start point and parsing #
###########################

def startup_parsing() -> Tuple[str, str]:
    """Parses the startup command arguments.

    Returns:
        Tuple[str, str]: The configuration file path and the log level.
        log level is set to "INFO" if not specified.
    """

    parser = argparse.ArgumentParser(
        description="Taskmaster is a program that manages other programs."
    )
    parser.add_argument(
        "filename", type=str, help="The path to the configuration file."
    )
    parser.add_argument(
        "-l",
        "--logLevel",
        help="Set the log level. INFO if not specified.",
        action="store",
        default="INFO",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    args = parser.parse_args()
    return args.filename, args.logLevel


def taskmasterd() -> None:

    config_file, log_level = startup_parsing()  # log_level = "INFO" if not specified
    logger.setLevel(log_level)

    try:
        config = load_config(config_file)
        validateConfig(config)
    except Exception as e:
        logger.error(e)
        print(f"ERROR: failed to start taskmaster: {e}")
        exit(1)

    # refer to the existing global variable
    global master
    master = MasterCtl(config_file, config)

    init_signal_handling()
    master.init_services()
    logger.info(f"Taskmaster is running - pid: {master.pid}")
    run_server()


if __name__ == "__main__":
    taskmasterd()
