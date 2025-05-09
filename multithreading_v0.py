import threading
import time
import requests

def download_site(url):
    response = requests.get(url)
    print(f"Descargados {len(response.content)} bytes de {url}")

def download_all_sites(sites):
    threads = []
    for url in sites:
        thread = threading.Thread(target=download_site, args=(url,))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    sites = [
        "https://www.python.org",
        "https://www.google.com",
        "https://www.github.com"
    ] * 5
    
    start_time = time.time()
    download_all_sites(sites)
    duration = time.time() - start_time
    print(f"Descargados {len(sites)} sitios en {duration:.2f} segundos")
    