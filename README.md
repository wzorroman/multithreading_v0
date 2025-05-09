# multithreading_v0


### asyncio_v1.py
   Ejemplo basico, Si trabajas con muchas operaciones de red

### asyncio_v2.py
  (Web Scraper Asíncrono)
   Este ejemplo implementa:
   1. Descarga concurrente de páginas web
   2. Procesamiento del HTML descargado
   3. Limitación de tasa (rate limiting)
   4. Manejo de errores robusto
   5. Progreso en tiempo real

### asyncio_v3.py
 Combinando asyncio con Multiprocessing, este ejemplo muestra cómo combinar la eficiencia de asyncio para I/O con el poder de multiprocessing para CPU-bound tasks, implementando:
  1. Un servidor HTTP asíncrono que maneja múltiples solicitudes
  2. Un pool de procesos para tareas intensivas de CPU 
  3. Comunicación bidireccional entre los procesos
  4. Sistema de colas para distribuir el trabajo
  5. Monitoreo en tiempo real del progreso
