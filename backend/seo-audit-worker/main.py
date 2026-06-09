import asyncio
from app.workers.queue_consumer import run_consumer
from app.workers.submit_consumer import run_submit_consumer

async def start_all():
    print("Khởi chạy đồng thời Audit Consumer và Submit Consumer...")
    await asyncio.gather(
        run_consumer(),
        run_submit_consumer()
    )

if __name__ == "__main__":
    asyncio.run(start_all())