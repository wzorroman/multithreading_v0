# Ejemplo: Calcular números primos (CPU-bound)
import multiprocessing
import time

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def count_primes(start, end):
    return sum(1 for num in range(start, end) if is_prime(num))

if __name__ == "__main__":
    start = time.time()
    
    # Dividimos el trabajo en 4 procesos
    ranges = [(1, 25_000), (25_000, 50_000), (50_000, 75_000), (75_000, 100_000)]
    
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.starmap(count_primes, ranges)
    
    total_primes = sum(results)
    print(f"Total de primos: {total_primes}")
    print(f"Tiempo con multiprocessing: {time.time() - start:.2f} segundos")
    