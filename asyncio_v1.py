# asyncio (Para E/S asíncrona)
# Si trabajas con muchas operaciones de red, asyncio puede ser más 
# eficiente que multithreading
import aiohttp
import asyncio

async def download_async(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.read()
            print(f"Descargados {len(content)} bytes de {url}")

async def main():
    tasks = [download_async(url) for url in urls]
    await asyncio.gather(*tasks)

asyncio.run(main())
