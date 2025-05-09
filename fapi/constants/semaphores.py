import asyncio

SEMAPHORE_DETAILS = asyncio.Semaphore(60)  
SEMAPHORE_PHOTOS = asyncio.Semaphore(60) 