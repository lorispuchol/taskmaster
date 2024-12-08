import logging
import os
import pathlib


# Create the path to the log file directory alongside the src directory
PATH_LOG_FILE: str = pathlib.Path(__file__).parent.parent / "log/taskmaster.log"
if not os.path.exists(PATH_LOG_FILE):
    PATH_LOG_FILE.parent.mkdir(exist_ok=True, parents=True)

# Clear the log file thanks to the 'w' mode (overwrite)
open(PATH_LOG_FILE, "w").close()

# Configure the logger
# Logs are appends in the log file ('a' mode)
logging.basicConfig(
    filename=PATH_LOG_FILE,
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create a shared logger instance
logger: logging.Logger = logging.getLogger("BIG-LOGGER")

# Set the logger level to DEBUG - Overwrited by the user input <loglevel> options in <starting> function
logger.setLevel(logging.DEBUG)