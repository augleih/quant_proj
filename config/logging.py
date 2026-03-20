from loguru import logger
import sys
import os
from config.settings import LOG_LEVEL, LOG_DIR

# Remove default handler
logger.remove()

# Console output
logger.add(sys.stderr, level=LOG_LEVEL,
           format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | {message}")

# File output
os.makedirs(LOG_DIR, exist_ok=True)
logger.add(os.path.join(LOG_DIR, "qt_{time}.log"),
           level=LOG_LEVEL, rotation="10 MB", retention="7 days")
