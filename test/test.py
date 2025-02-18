import sys
import subprocess
import select
import shlex

managed_processes = []

def process_command(line):
    tokens = shlex.split(line)
    if not tokens:
        return
    
    cmd = tokens[0]
    
    if cmd == "start":
        autorestart = False
        args = tokens[1:]
        
        # Parse options
        i = 0
        while i < len(args):
            if args[i] == "--autorestart":
                autorestart = True
                i += 1
            else:
                break
        
        command = args[i:]
        if not command:
            print("Error: No command provided")
            return
        
        try:
            proc = subprocess.Popen(command, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        except Exception as e:
            print(f"Error starting process: {e}")
            return
        
        managed_processes.append({
            "proc": proc,
            "command": command,
            "autorestart": autorestart
        })
        print(f"Started process {proc.pid}")

    elif cmd == "stop":
        if len(tokens) < 2:
            print("Error: PID required for stop command")
            return
        
        try:
            pid = int(tokens[1])
        except ValueError:
            print("Error: Invalid PID")
            return
        
        found = False
        for entry in managed_processes[:]:
            if entry["proc"].pid == pid:
                entry["proc"].terminate()
                try:
                    entry["proc"].wait(timeout=1)
                except subprocess.TimeoutExpired:
                    entry["proc"].kill()
                    entry["proc"].wait()
                managed_processes.remove(entry)
                print(f"Stopped process {pid}")
                found = True
                break
        if not found:
            print(f"No process with PID {pid} found")

    elif cmd == "status":
        if not managed_processes:
            print("No managed processes")
            return
        
        for entry in managed_processes:
            proc = entry["proc"]
            status = proc.poll()
            status_str = "running" if status is None else f"exited ({status})"
            print(f"PID: {proc.pid:6} | Command: {' '.join(entry['command'])} | Autorestart: {entry['autorestart']} | Status: {status_str}")

    elif cmd == "exit":
        for entry in managed_processes:
            entry["proc"].terminate()
            try:
                entry["proc"].wait(timeout=1)
            except subprocess.TimeoutExpired:
                entry["proc"].kill()
                entry["proc"].wait()
        print("Exiting process manager")
        sys.exit(0)

    else:
        print(f"Unknown command: {cmd}")

def check_processes():
    for entry in managed_processes[:]:
        proc = entry["proc"]
        status = proc.poll()
        if status is not None:
            if entry["autorestart"]:
                print(f"Process {proc.pid} exited. Restarting...")
                try:
                    new_proc = subprocess.Popen(entry["command"], stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                except Exception as e:
                    print(f"Error restarting process: {e}")
                    managed_processes.remove(entry)
                    continue
                entry["proc"] = new_proc
            else:
                managed_processes.remove(entry)
                print(f"Removed exited process {proc.pid}")


import readline

def main():
    print("Process manager started. Available commands:")
    print("  start [--autorestart] <command>")
    print("  stop <pid>")
    print("  status")
    print("  exit")
    
    timeout: bool = False
    while True:
        if timeout == False:
            sys.stdout.write("Enter command: ")  # Display prompt
            sys.stdout.flush()
        rlist, _, _ = select.select([sys.stdin], [], [], 1.0)
        if rlist:
            timeout = False
            line = sys.stdin.readline().strip()
            if not line:
                continue
            process_command(line)
        else:
            timeout = True
            check_processes()

if __name__ == "__main__":
    main()