
import logging

from data_slicer import set_up_logging
from data_slicer.utilities import TracedVariable

# Set up logging
#logger = logging.getLogger('ds')
#logger.setLevel(logging.DEBUG)
#console_handler = logging.StreamHandler()
#console_handler.setLevel(logging.DEBUG)
#formatter = logging.Formatter('[%(levelname)s][%(name)s]%(message)s')
#console_handler.setFormatter(formatter)
#logger.addHandler(console_handler)
#logger.propagate = False

tv = TracedVariable(value=5)

tv.get_value()
tv.set_value(8)
tv.get_value()
