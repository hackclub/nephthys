import inspect
import logging
from contextlib import asynccontextmanager
from time import perf_counter

from prometheus_client import Histogram

# Mostly the default buckets, but with some of the larger ones removed
BUCKETS = (
    0.005,
    0.01,
    0.025,
    0.05,
    0.075,
    0.1,
    0.25,
    0.5,
    0.75,
    1.0,
    2.5,
    5.0,
    10.0,
    float("inf"),
)

CODE_BLOCK_DURATION = Histogram(
    "nephthys_code_block_duration_seconds",
    "How long a labelled block of code takes to execute",
    ["code_block"],
    buckets=BUCKETS,
)


@asynccontextmanager
async def perf_timer(name: str, metric_label: str | None = None, **metric_labels):
    start_time = perf_counter()
    yield
    duration = perf_counter() - start_time
    # Get the name of the function that called the `perf_timer()`
    function_name = inspect.stack()[2].function
    logging.debug(f"{function_name}: {name} took {duration:.3f}s")
    if metric_label:
        CODE_BLOCK_DURATION.labels(metric_label, **metric_labels).observe(duration)
