"""
Main script for dashboard project. pulls together and runs the various modules
"""
from pipeline_code import (
    acquire_data,
    per_fighter_pipeline,
    logger_module,
)
import time


logger = logger_module.get_pipeline_logger(__name__, filename=time.strftime('%d%m%y_%H%M%S'))


def main(
    acquisition: bool = True
) -> None:
    """Run the bloody thing.

    Parameters
    ----------
    acquisition : Set True to run the acquisition / data transformation modules.
    """
    logger.info('Beginning dashboard run')

    if acquisition:
        acquire_data.acquire_data_main()
        per_fighter_pipeline.per_fighter_pipeline_main()
        logger.info('Completed data acquisition and transformation')

    print('heres where id keep my dashboard, if i had one.')


if __name__ == '__main__':
    main(acquisition=True)
