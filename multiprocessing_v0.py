import multiprocessing
import time

def cpu_bound(number):
    return sum(i * i for i in range(number))

def calculate_all(numbers):
    with multiprocessing.Pool() as pool:
        pool.map(cpu_bound, numbers)

if __name__ == "__main__":
    numbers = [5_000_000 + x for x in range(5)]
    
    start_time = time.time()
    calculate_all(numbers)
    duration = time.time() - start_time
    print(f"Calculado en {duration:.2f} segundos")
    