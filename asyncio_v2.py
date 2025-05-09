# (Web Scraper Asíncrono)
# Este ejemplo implementa:
# Descarga concurrente de páginas web
# Procesamiento del HTML descargado
# Limitación de tasa (rate limiting)
# Manejo de errores robusto
# Progreso en tiempo real

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import time
from collections import Counter
from tqdm.asyncio import tqdm_asyncio

class AsyncWebScraper:
    def __init__(self, max_concurrent=10, request_timeout=10):
        self.max_concurrent = max_concurrent
        self.request_timeout = aiohttp.ClientTimeout(total=request_timeout)
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.word_counter = Counter()
    
    async def fetch_page(self, session, url):
        async with self.semaphore:  # Limitar concurrencia
            try:
                async with session.get(url, timeout=self.request_timeout) as response:
                    if response.status == 200:
                        return await response.text()
                    return None
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                print(f"Error al descargar {url}: {str(e)}")
                return None
    
    async def process_page(self, session, url):
        html = await self.fetch_page(session, url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            words = soup.get_text().split()
            self.word_counter.update(words)
            return len(words)
        return 0
    
    async def scrape_sites(self, urls):
        connector = aiohttp.TCPConnector(limit=self.max_concurrent)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [self.process_page(session, url) for url in urls]
            
            # Usar tqdm para mostrar progreso
            results = await tqdm_asyncio.gather(
                *tasks,
                desc="Scrapeando sitios",
                unit="página"
            )
            
            total_words = sum(results)
            return total_words
    
    def get_top_words(self, n=10):
        return self.word_counter.most_common(n)

async def advanced_async_example():
    urls = [
        "https://python.org",
        "https://docs.python.org/3/library/asyncio.html",
        "https://aiohttp.readthedocs.io/",
        "https://realpython.com/async-io-python/",
        "https://en.wikipedia.org/wiki/Asynchronous_I/O",
        "https://www.twilio.com/blog/asynchronous-http-requests-in-python-with-aiohttp",
        "https://www.artima.com/articles/inside-python-asyncio",
        "https://bbc.com",
        "https://news.ycombinator.com",
        "https://github.com",
        "https://stackoverflow.com",
        "https://reddit.com",
        "https://medium.com",
        "https://dev.to",
        "https://pypi.org"
    ] * 2  # Duplicamos para tener más trabajo
    
    scraper = AsyncWebScraper(max_concurrent=5, request_timeout=15)
    
    print("Iniciando scraping asíncrono...")
    start_time = time.time()
    total_words = await scraper.scrape_sites(urls)
    duration = time.time() - start_time
    
    print("\nEstadísticas:")
    print(f"- Total de páginas procesadas: {len(urls)}")
    print(f"- Total de palabras analizadas: {total_words}")
    print(f"- Tiempo total: {duration:.2f} segundos")
    print(f"- Tasa: {len(urls)/duration:.2f} páginas/segundo")
    
    print("\nPalabras más comunes:")
    for word, count in scraper.get_top_words(10):
        print(f"{word}: {count}")

if __name__ == '__main__':
    # Para Python 3.7+
    asyncio.run(advanced_async_example())
    
    # Para versiones anteriores:
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(advanced_async_example())
    # loop.close()
    