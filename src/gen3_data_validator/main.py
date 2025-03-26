from src.logging_config import configure_logging
import logging

configure_logging()
logger = logging.getLogger(__name__)

def main():
    logger.info("Application started")
    # Call other modules/functions here
    logger.info("Application finished")

if __name__ == "__main__":
    main()
