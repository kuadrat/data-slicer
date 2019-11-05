"""
This file is intended to be imported by scripts that want to output logging 
info of all the components they use.
"""

import logging

# Set up logging
logger = logging.getLogger('ds')
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s][%(name)s]%(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.propagate = False

