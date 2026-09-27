import time
from functools import wraps
from openai import APIConnectionError, APITimeoutError, RateLimitError, InternalServerError

TRANSIENT = (APIConnectionError, APITimeoutError, RateLimitError, InternalServerError)

def retry_openai(attempts=3, base_delay=0.8):
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            for attempt in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except TRANSIENT:
                    if attempt == attempts - 1:
                        raise
                    time.sleep(base_delay * (2 ** attempt))
        return wrapped
    return decorator
