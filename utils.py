import time
import logging

log = logging.getLogger(__name__)

# Decorator to time a function
def timeit(func):
    def timed(*args, **kwargs):
        time_start = time.time()
        result = func(*args, **kwargs)
        _yellow = "\x1b[33;20m"
        _reset = "\x1b[0m"
        _msg = f"{_yellow}{func.__name__} duration: {time.time() - time_start:.2f} seconds{_reset}"
        log.info(_msg)
        return result
    return timed
