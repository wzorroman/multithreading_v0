# Ejemplo con ThreadPoolExecutor (I/O-bound)
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(download, urls)

# Ejemplo con ProcessPoolExecutor (CPU-bound)
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor(max_workers=4) as executor:
    executor.map(count_primes, ranges)