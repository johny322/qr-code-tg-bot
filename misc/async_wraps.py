import asyncio
import concurrent.futures


async def run_blocking_io(func, *args):
    """Запуск синхронной функции асинхронно"""
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool, func, *args
        )
        return result


async def run_blocking_cpu(func, *args):
    """Запуск синхронной функции асинхронно"""
    loop = asyncio.get_running_loop()
    with concurrent.futures.ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool, func, *args
        )
        return result
