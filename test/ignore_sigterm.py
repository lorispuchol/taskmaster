import signal
import time


def handle_sigterm(signum, frame):
    print("Received SIGTERM, but ignoring it!")


# Ignore SIGTERM signal
signal.signal(signal.SIGTERM, handle_sigterm)

print("Running an infinite loop. Press Ctrl+C or send SIGINT to exit.")

while True:
    try:
        time.sleep(1)  # Sleep to prevent high CPU usage
    except KeyboardInterrupt:
        print("Exiting on user request (Ctrl+C OR SIGINT).")
        exit(2)
