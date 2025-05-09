# Combinando asyncio con Multiprocessing
# Este ejemplo muestra cómo combinar la eficiencia de asyncio para I/O con el 
# poder de multiprocessing para CPU-bound tasks, implementando:

# 1. Un servidor HTTP asíncrono que maneja múltiples solicitudes
# 2. Un pool de procesos para tareas intensivas de CPU
# 3. Comunicación bidireccional entre los procesos
# 4. Sistema de colas para distribuir el trabajo
# 5. Monitoreo en tiempo real del progreso

import asyncio
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import aiohttp
from aiohttp import web
import json
import time
from uuid import uuid4

# =============================================
# Parte CPU-bound (se ejecuta en procesos)
# =============================================
def cpu_intensive_task(task_data):
    """Simula una tarea intensiva de CPU con progreso reportable"""
    result = 0
    steps = task_data.get('steps', 100)
    progress_queue = task_data['progress_queue']
    
    for i in range(1, steps + 1):
        # Simular trabajo de CPU
        result += sum(x*x for x in range(1, 10000))
        
        # Reportar progreso
        if i % 10 == 0 or i == steps:
            progress_queue.put({
                'task_id': task_data['task_id'],
                'progress': i/steps * 100,
                'step': i,
                'result_partial': result
            })
    
    return {
        'task_id': task_data['task_id'],
        'result': result,
        'status': 'completed'
    }

def process_worker(task_queue, result_queue, progress_queue):
    """Worker que ejecuta tareas CPU-bound en procesos separados"""
    while True:
        task_data = task_queue.get()
        if task_data is None:  # Señal de terminación
            break
            
        # Añadir cola de progreso a los datos de la tarea
        task_data['progress_queue'] = progress_queue
        result = cpu_intensive_task(task_data)
        result_queue.put(result)

# =============================================
# Parte asíncrona (servidor web + coordinación)
# =============================================
async def start_process_pool(num_workers):
    """Inicia el pool de procesos y las colas de comunicación"""
    task_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()
    progress_queue = multiprocessing.Queue()
    
    # Iniciar workers
    workers = []
    for _ in range(num_workers):
        p = multiprocessing.Process(
            target=process_worker,
            args=(task_queue, result_queue, progress_queue)
        )
        p.start()
        workers.append(p)
    
    return {
        'task_queue': task_queue,
        'result_queue': result_queue,
        'progress_queue': progress_queue,
        'workers': workers
    }

async def monitor_progress(app):
    """Corutina que monitorea el progreso y actualiza el estado"""
    while True:
        try:
            progress = app['progress_queue'].get_nowait()
            task_id = progress['task_id']
            
            # Actualizar estado en memoria
            if task_id in app['tasks']:
                app['tasks'][task_id]['progress'] = progress['progress']
                app['tasks'][task_id]['last_update'] = time.time()
                
                # Almacenar resultados parciales si es necesario
                if 'partial_results' not in app['tasks'][task_id]:
                    app['tasks'][task_id]['partial_results'] = []
                app['tasks'][task_id]['partial_results'].append(progress)
                
                print(f"Progreso actualizado: {task_id} - {progress['progress']:.1f}%")
        except:
            await asyncio.sleep(0.1)

async def handle_start_task(request):
    """Endpoint para iniciar una nueva tarea"""
    app = request.app
    data = await request.json()
    
    task_id = str(uuid4())
    steps = data.get('steps', 100)
    
    # Crear entrada de tarea
    app['tasks'][task_id] = {
        'start_time': time.time(),
        'progress': 0,
        'status': 'queued',
        'steps': steps
    }
    
    # Enviar tarea al pool de procesos
    app['task_queue'].put({
        'task_id': task_id,
        'steps': steps
    })
    
    print(f"Nueva tarea iniciada: {task_id}")
    
    return web.json_response({
        'task_id': task_id,
        'status': 'queued'
    })

async def handle_check_status(request):
    """Endpoint para verificar el estado de una tarea"""
    app = request.app
    task_id = request.match_info['task_id']
    
    if task_id not in app['tasks']:
        return web.json_response(
            {'error': 'Task not found'}, 
            status=404
        )
    
    task_data = app['tasks'][task_id]
    
    # Verificar si hay resultados finales
    try:
        result = app['result_queue'].get_nowait()
        if result['task_id'] == task_id:
            task_data.update(result)
            task_data['end_time'] = time.time()
    except:
        pass
    
    return web.json_response(task_data)

async def background_result_processor(app):
    """Procesa resultados finales en segundo plano"""
    while True:
        try:
            result = app['result_queue'].get_nowait()
            task_id = result['task_id']
            
            if task_id in app['tasks']:
                app['tasks'][task_id].update(result)
                app['tasks'][task_id]['end_time'] = time.time()
                print(f"Tarea completada: {task_id}")
        except:
            await asyncio.sleep(0.5)

async def startup(app):
    """Configuración inicial de la aplicación"""
    # Iniciar pool de procesos
    pool = await start_process_pool(num_workers=multiprocessing.cpu_count())
    app.update(pool)
    app['tasks'] = {}
    
    # Iniciar tareas en segundo plano
    app['progress_monitor'] = asyncio.create_task(monitor_progress(app))
    app['result_processor'] = asyncio.create_task(background_result_processor(app))

async def cleanup(app):
    """Limpieza al cerrar la aplicación"""
    # Detener monitores
    app['progress_monitor'].cancel()
    app['result_processor'].cancel()
    
    # Detener workers
    for _ in range(len(app['workers'])):
        app['task_queue'].put(None)
    
    for worker in app['workers']:
        worker.join()

def create_app():
    """Configura la aplicación web"""
    app = web.Application()
    app.add_routes([
        web.post('/task', handle_start_task),
        web.get('/task/{task_id}', handle_check_status)
    ])
    
    app.on_startup.append(startup)
    app.on_cleanup.append(cleanup)
    
    return app

# =============================================
# Ejecución principal
# =============================================
if __name__ == '__main__':
    # Configuración para sistemas Windows
    if multiprocessing.get_start_method() == 'fork':
        multiprocessing.set_start_method('spawn')
    
    # Iniciar servidor web
    web.run_app(create_app(), port=8080)