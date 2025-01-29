import logging
import os
import pathlib


# Create log directory alongside src directory
PATH_LOG_FILE: str = pathlib.Path(__file__).parent.parent.parent / "log/taskmaster.log"
if not os.path.exists(PATH_LOG_FILE):
    PATH_LOG_FILE.parent.mkdir(exist_ok=True, parents=True)

# Clear the log file
# 'w' for overwrite mode
open(PATH_LOG_FILE, "w").close()

# 'a' for append mode
logging.basicConfig(
    filename=PATH_LOG_FILE,
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d %b %H:%M:%S"
)

# Create a shared logger instance
logger: logging.Logger = logging.getLogger("BIG-LOGGER")

# Set to DEBUG by default
# Overwrited by the user input <logLevel> in taskmaster()
logger.setLevel(logging.DEBUG)
