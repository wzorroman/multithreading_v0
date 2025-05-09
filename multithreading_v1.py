# Descargar múltiples páginas web (I/O-bound)
import threading
import requests
import time

def download(url):
    response = requests.get(url)
    print(f"Descargados {len(response.content)} bytes de {url}")

urls = [
    "https://www.python.org",
    "https://www.google.com",
    "https://www.github.com"
] * 3

# Usando hilos
start = time.time()
threads = []
for url in urls:
    thread = threading.Thread(target=download, args=(url,))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

print(f"Tiempo con hilos: {time.time() - start:.2f} segundos")