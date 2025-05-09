# Ejemplo Avanzado con concurrent.futures (Combinando ThreadPool y ProcessPool)
# Este ejemplo muestra cómo manejar simultáneamente:
# Tareas CPU-intensivas con ProcessPool
# Tareas I/O-intensivas con ThreadPool
# Recolectar y procesar resultados combinados

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import requests
import math
import time
import os

# Función CPU-bound (procesamiento de imágenes simulado)
def process_image(image_id):
    print(f"Procesando imagen {image_id} en proceso {os.getpid()}")
    time.sleep(0.5)  # Simula procesamiento pesado
    return f"imagen_{image_id}_procesada.jpg"

# Función I/O-bound (descarga de metadatos)
def fetch_metadata(url):
    print(f"Descargando {url} en hilo...")
    response = requests.get(url, timeout=5)
    time.sleep(1)  # Simula latencia de red
    return {
        'url': url,
        'status': response.status_code,
        'content_type': response.headers.get('Content-Type')
    }

def advanced_concurrent_example():
    # URLs para descargar metadatos
    api_urls = [
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/comments/1",
        "https://jsonplaceholder.typicode.com/albums/1"
    ]
    
    # IDs de imágenes para procesar
    image_ids = list(range(1, 6))
    
    final_results = {}
    
    with ThreadPoolExecutor(max_workers=3) as thread_pool, \
         ProcessPoolExecutor(max_workers=2) as process_pool:
        
        # Lanzar todas las tareas
        future_to_key = {}
        
        # Tareas I/O-bound
        for url in api_urls:
            future = thread_pool.submit(fetch_metadata, url)
            future_to_key[future] = ('metadata', url)
        
        # Tareas CPU-bound
        for img_id in image_ids:
            future = process_pool.submit(process_image, img_id)
            future_to_key[future] = ('image', img_id)
        
        # Procesar resultados conforme van llegando
        for future in as_completed(future_to_key):
            task_type, identifier = future_to_key[future]
            try:
                result = future.result()
                if task_type == 'metadata':
                    final_results[f'metadata_{identifier}'] = result
                else:
                    final_results[f'image_{identifier}'] = result
            except Exception as e:
                print(f"Error en tarea {identifier}: {str(e)}")
    
    return final_results

if __name__ == '__main__':
    start_time = time.time()
    results = advanced_concurrent_example()
    print("\nResultados finales:")
    for key, value in results.items():
        print(f"{key}: {str(value)[:80]}...")
    print(f"\nTiempo total: {time.time() - start_time:.2f} segundos")
