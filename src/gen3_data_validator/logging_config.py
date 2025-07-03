import logging
from datetime import datetime


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=f"../logs/{datetime.now()}.log",
        filemode='x',
        force=True  # Ensures custom configuration takes effect
    )
    logging.info("This log should appear in logs.log")
