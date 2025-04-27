import os

from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor



DEFAULT_THREAD_POOL=ThreadPoolExecutor(
    max_workers=min(32,(os.cpu_count() or 1)+4)
)

DEFAULT_PROCESS_POOL=ProcessPoolExecutor(
       max_workers=(os.cpu_count() or 1)
)