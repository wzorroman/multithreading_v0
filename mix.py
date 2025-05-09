import concurrent.futures
import requests
import math

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def process_prime_task(start_end):
    start, end = start_end
    return sum(1 for num in range(start, end) if is_prime(num))

def download_site(url):
    response = requests.get(url)
    return len(response.content)

def main():
    # Parte CPU-bound (multiprocessing)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        ranges = [(i*10_000, (i+1)*10_000) for i in range(10)]
        prime_counts = list(executor.map(process_prime_task, ranges))
        total_primes = sum(prime_counts)
        print(f"Total de primos encontrados: {total_primes}")

    # Parte I/O-bound (multithreading)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        sites = ["https://www.python.org"] * 10
        byte_counts = list(executor.map(download_site, sites))
        total_bytes = sum(byte_counts)
        print(f"Total de bytes descargados: {total_bytes}")

if __name__ == "__main__":
    main()
