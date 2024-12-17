from typing import Callable
import time
from random import random


def delay_request(delay: int = 0, random_delay: int = 0) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            time.sleep(delay + random_delay * random())
            return func(*args, **kwargs)

        return wrapper

    return decorator
