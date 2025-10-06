import logging.config
import yaml
from pathlib import Path
from controller import MainController

log_config_path = Path("logging.yaml")
with open(log_config_path, "r") as f:
    config = yaml.safe_load(f.read())
logging.config.dictConfig(config)

logger = logging.getLogger("Main")
logger.info("Application started")

if __name__ == "__main__":
    controller = MainController()
    logger.info("Processing files started")
    controller.process_files()
    logger.info("Processing files finished")
