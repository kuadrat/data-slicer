import logging

from data_slicer import set_up_logging

logger = logging.getLogger('ds.'+__name__)

def test_logging() :
    logger.info('Testing logging.')

if __name__ == "__main__" :
    test_logging()        
