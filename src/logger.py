import logging

# Configure the logger
logging.basicConfig(
    filename='log/taskmaster.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create a shared logger instance
logger: logging.Logger = logging.getLogger("LOGGER")