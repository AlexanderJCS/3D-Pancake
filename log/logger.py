# Description: This file contains the logger configuration for the application. Any module that needs to log messages
#  should import the logger from this file.

import logging
import os

# Configure the logger
logger = logging.getLogger("3d_pancake")
logger.setLevel(logging.DEBUG)

# Create handlers
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../3d_pancake.log"))

console_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
