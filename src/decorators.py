import time
import logging
import functools
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log_execution_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        stop = time.perf_counter()
        duration = stop - start
        logger.info(f"Function '{func.__name__}' took {duration:.4f} seconds!")
        return result
    return wrapper

def handle_aws_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"AWS ClientError in '{func.__name__}': {error_code} - {e}")
            return None
        except BotoCoreError as e:
            logger.error(f"AWS Connection Error in '{func.__name__}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected Error in '{func.__name__}': {e}")
            raise
    return wrapper