import logging, os, pathlib, sys

# Create a shared logger instance
logger: logging.Logger = logging.getLogger("BIG-LOGGER")

# Set to INFO by default
# Overwrited by the user input <logLevel> in taskmaster()
logger.setLevel(logging.INFO)

logger.propagate = False  # Prevent propagation to the root logger


# Create log directory alongside src directory
PATH_LOG_FILE: str = pathlib.Path(__file__).parent.parent.parent / "log/taskmaster.log"
if not os.path.exists(PATH_LOG_FILE):
    PATH_LOG_FILE.parent.mkdir(exist_ok=True, parents=True)

# Clear the log file
# 'w' for overwrite mode

try:
    open(PATH_LOG_FILE, "w").close()
except Exception as e:
    print(f"Failed to access log file <{PATH_LOG_FILE}>: {e}")
    sys.exit(1)

if not logger.handlers:
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%d %b %H:%M:%S"
    )

    # Create file handler
    file_handler = logging.FileHandler(PATH_LOG_FILE)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Create stdout handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
