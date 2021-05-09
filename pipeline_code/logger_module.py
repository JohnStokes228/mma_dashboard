"""
Logging module for dashboard pipeline, to be called at specific stages only. This needs to exist since we have
web scraped data involved and don't want to accidentally shag ourselves on the output. We may further edit this over
time but for now this will do i guess lad.

TODO: - implement logging to terminal as well as logging to logfile
"""
import logging
import time


def get_pipeline_logger(name):
    """Create logger instance for the pipeline using desired settings.
`
    Parameters
    ----------
    name : Logger name, typically given value of __name__ from file logger called.

    Returns
    -------
    Logger obj.
    """
    file_handler = logging.FileHandler('run_logs/{}_runlog.log'.format(time.strftime('%d%m%y_%H%M%S')))
    formatter = logging.Formatter(fmt='%(asctime)s\t%(levelname)s\t%(module)s\t%(funcName)s\t%(message)s',
                                  datefmt='%d-%m-%Y %H:%M:%S')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    logger = logging.getLogger(name)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    return logger
