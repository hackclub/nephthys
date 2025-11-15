import inspect
import logging
from contextlib import asynccontextmanager
from time import perf_counter


@asynccontextmanager
async def perf_timer(name: str):
    start_time = perf_counter()
    yield
    duration = perf_counter() - start_time
    # Get the name of the function that called the `perf_timer()`
    function_name = inspect.stack()[2].function
    logging.debug(f"{function_name}: {name} took {duration:.3f}s")
