import socket, selectors, signal, sys, argparse, os, datetime
from typing import List, Tuple, Dict

####################
# Global variables #
####################

sel = selectors.DefaultSelector()
shutdown_flag = False


def load_modules():
    global logger, MasterCtl, load_config, validateConfig, State, AutoRestart, Service, ServiceState, Color
    from utils.colors import Color
    from logger import logger
    from masterctl import MasterCtl
    from service import Service, ServiceState
    from process import State
    from service import AutoRestart
    from config import load_config, validateConfig


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


##############
# monitoring #
##############


def process_monitoring():

    services_ready_to_remove: List[Service] = []  # After a reload request
    services_ready_to_update: List[Service] = []  # After a reload request
    services_ready_to_restart: List[Service] = []  # After a restart request

    ## Manage Reload and Restart
    for service in master.services.values():
        ## Services removed
        if service.state == ServiceState.REMOVING:
            isReady: bool = False
            for process in service.processes:
                if (
                    process.state == State.STARTING
                    or process.state == State.STOPPING
                    or process.state == State.RUNNING
                ):
                    isReady = False
                    break
                else:
                    isReady = True
            if isReady:
                services_ready_to_remove.append(service)

        ## Services updated
        if service.state == ServiceState.UPDATING:
            isReady: bool = False
            for process in service.processes:
                if (
                    process.state == State.STARTING
                    or process.state == State.STOPPING
                    or process.state == State.RUNNING
                ):
                    isReady = False
                    break
                else:
                    isReady = True
            if isReady:
                services_ready_to_update.append(service)

        ## Services restarted
        if service.state == ServiceState.RESTARTING:
            isReady: bool = False
            for process in service.processes:
                if (
                    process.state == State.STARTING
                    or process.state == State.STOPPING
                    or process.state == State.RUNNING
                ):
                    isReady = False
                    break
                else:
                    isReady = True
            if isReady:
                services_ready_to_restart.append(service)

        for process in service.processes:
            ## Check BACKOFF process
            if process.proc is None and process.state == State.BACKOFF:
                if process.current_retry > service.startretries:
                    logger.critical(f"{process.name}: reached maximum retries")
                    process.state = State.FATAL
                    process.changedate = datetime.datetime.now()
                    process.current_retry = 1
                elif datetime.datetime.now() - process.changedate > datetime.timedelta(
                    seconds=process.current_retry
                ):
                    logger.info(
                        f"{process.name}: retrying to start ({process.current_retry})"
                    )
                    process.start()
                    process.current_retry += 1

            ## Check EXITED process
            if process.proc is not None and process.state == State.EXITED:
                if service.autorestart == AutoRestart.ALWAYS.value:
                    # process.proc = None
                    try:
                        logger.info(f"{process.name}: unconditional restart")
                        process.start()
                    except Exception as e:
                        logger.critical(f"{process.name} Error restarting: {e}")
                elif (
                    service.autorestart == AutoRestart.UNEXPECTED.value
                    and abs(process.proc.returncode) not in service.exitcodes
                ):
                    # process.proc = None
                    try:
                        logger.info(f"{process.name}: conditional restart")
                        process.start()
                    except Exception as e:
                        logger.critical(
                            f"{process.name}: Error restarting process: {e}"
                        )
                else:
                    process.proc = None

            ## Check RUNNING process
            if process.proc is not None and process.state == State.RUNNING:
                process.proc.poll()
                if process.proc.returncode is not None:
                    process.state = State.EXITED
                    process.changedate = datetime.datetime.now()
                    if abs(process.proc.returncode) in service.exitcodes:
                        logger.error(
                            f"{process.name}: {process.proc.pid} exited expectedly with code {abs(process.proc.returncode)}"
                        )
                    else:
                        logger.error(
                            f"{process.name}: {process.proc.pid} exited unexpectedly with code {abs(process.proc.returncode)}"
                        )
                    process.current_retry = 1

            ## Check STARTING process
            if process.proc is not None and process.state == State.STARTING:
                process.proc.poll()
                # Success
                if (
                    process.proc.returncode is None
                    and datetime.datetime.now() - process.changedate
                    >= datetime.timedelta(seconds=service.starttime)
                ):
                    process.state = State.RUNNING
                    process.changedate = datetime.datetime.now()
                    logger.info(
                        f"{process.name}: {process.proc.pid} is in running state for now"
                    )
                    process.current_retry = 1
                # Success but exited immediatly
                elif (
                    process.proc.returncode is not None
                    and datetime.datetime.now() - process.changedate
                    >= datetime.timedelta(seconds=service.starttime)
                ):
                    process.state = State.EXITED
                    process.changedate = datetime.datetime.now()
                    if abs(process.proc.returncode) in service.exitcodes:
                        logger.error(
                            f"{process.name}: {process.proc.pid} exited expectedly with code {abs(process.proc.returncode)} immediatly after enter in running state"
                        )
                    else:
                        logger.error(
                            f"{process.name}: {process.proc.pid} exited unexpectedly with code {abs(process.proc.returncode)} immediatly after enter in running state"
                        )
                    process.current_retry = 1

                # Failed before enter in running state
                elif (
                    process.proc.returncode is not None
                    and datetime.datetime.now() - process.changedate
                    < datetime.timedelta(seconds=service.starttime)
                ):
                    process.state = State.BACKOFF
                    process.changedate = datetime.datetime.now()
                    logger.error(
                        f"{process.name}: {process.proc.pid} failed with exit code {abs(process.proc.returncode)} during starting"
                    )
                    process.error_message = (
                        "Exited too quickly (process log may have details)"
                    )
                    process.proc = None

            ## Check STOPPING process
            if process.proc is not None and process.state == State.STOPPING:
                # If didn't stop after stop time
                if datetime.datetime.now() - process.changedate >= datetime.timedelta(
                    seconds=service.stoptime
                ):
                    logger.error(
                        f"{process.name}: {process.proc.pid} didn't stop in time"
                    )
                    process.kill()
                # If stopped before time
                else:
                    process.proc.poll()
                    if process.proc.returncode is not None:
                        process.state = State.STOPPED
                        process.changedate = datetime.datetime.now()
                        logger.info(
                            f"{process.name}: {process.proc.pid} has been stopped"
                        )
                        process.proc = None
        # Then: do nothing and wait for the next loop to check again

    # Remove services after reload
    for service in services_ready_to_remove:
        if master.services.get(service.name) is not None:
            master.services.get(service.name).state = ServiceState.NOTHING
            master.services.pop(service.name)
            logger.info(f"{service.name}: well terminated -> is no longer managed")

    # Update services after reload (remove then recreate)
    for service in services_ready_to_update:
        if master.services.get(service.name) is not None:
            serv_name: str = service.name
            for props in master.fullconfig["services"]:
                if props["name"] == serv_name:
                    new_props: Dict = props
            master.services.get(service.name).state = ServiceState.NOTHING
            master.services.pop(service.name)
            logger.info(f"{serv_name}: well terminated -> updating")
            master.services[serv_name] = Service(serv_name, new_props)

    for service in services_ready_to_restart:
        if master.services.get(service.name) is not None:
            master.services.get(service.name).state = ServiceState.NOTHING
            logger.info(f"{service.name}: well terminated -> restarting")
            master.services.get(service.name).start()


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


def handle_client(conn: socket.socket) -> None:
    addr = conn.getpeername()
    try:
        data = conn.recv(8192)
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


def accept_connection(sock):
    conn, addr = sock.accept()
    logger.info(f"Accept connection from {addr}")
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, data=handle_client)


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
            events = sel.select(timeout=0.005)
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
    logger.info(f"Taskmaster is running - pid: {master.pid}")
    master.init_services()
    run_server()


if __name__ == "__main__":
    try:
        test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        test.bind(("0.0.0.0", 65432))
    except Exception as e:
        print(f"Error: {e}")
        os._exit(1)
    else:
        test.close()
        load_modules()
        taskmasterd()
