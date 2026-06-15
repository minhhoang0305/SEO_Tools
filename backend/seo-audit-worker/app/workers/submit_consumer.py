import json
import asyncio
import aio_pika
import uuid
from app.core.config import RABBITMQ_HOST, DATABASE_URL
from app.repositories.postgres_repository import PostgresRepository
from app.engines.submit_platforms.factory import PlatformSubmitFactory

async def process_submit_job(message):
    job_id = message["JobId"]
    website_url = message["WebsiteUrl"]
    payload_str = message.get("Payload") or "{}"
    platforms = message.get("Platforms") or []
    mode = message.get("Mode") or "final"

    try:
        metadata = json.loads(payload_str)
    except Exception:
        metadata = {}

    print(f"\nProcessing Submit Job: {job_id} for URL: {website_url}")

    async with PostgresRepository(DATABASE_URL) as db_repo:
        # 1. Cập nhật trạng thái Job chính thành Running
        await db_repo.update_submit_job_status(job_id, "Running")
        
        all_success = True
        at_least_one_processed = False

        for platform_info in platforms:
            detail_id = platform_info["JobDetailId"]
            platform_code = platform_info["PlatformCode"]
            
            print(f"-> Submit lên Platform: {platform_code} (Detail ID: {detail_id})")
            
            await db_repo.update_submit_job_detail_status(detail_id, "Running")
            
            try:
                handler = PlatformSubmitFactory.get_submit_handler(platform_info, db_repo)
                at_least_one_processed = True
                
                result = await handler.submit(website_url, metadata, mode=mode)
                
                if result.get("success"):
                    await db_repo.update_submit_job_detail_status(
                        detail_id, 
                        "Success", 
                        response_data=result.get("response_data")
                    )
                else:
                    all_success = False
                    await db_repo.update_submit_job_detail_status(
                        detail_id, 
                        "Failed", 
                        error_message=result.get("error_message"),
                        response_data=result.get("response_data")
                    )
            except Exception as ex:
                all_success = False
                err_msg = f"Lỗi không mong muốn khi xử lý submit handler: {str(ex)}"
                print(err_msg)
                await db_repo.update_submit_job_detail_status(detail_id, "Failed", error_message=err_msg)
                await db_repo.save_submit_audit_log(detail_id, "SystemCrash", "Failed", err_msg)

        final_job_status = "Completed"
        if at_least_one_processed and not all_success:
            final_job_status = "Failed"
            
        await db_repo.update_submit_job_status(job_id, final_job_status)
        print(f"Finished Submit Job {job_id}. Final Status: {final_job_status}")


async def run_submit_consumer():
    connection = await aio_pika.connect_robust(
        host=RABBITMQ_HOST
    )

    async with connection:
        channel = await connection.channel()

        exchange = await channel.declare_exchange(
            "audit.exchange",
            type=aio_pika.ExchangeType.TOPIC,
            durable=True
        )

        queue = await channel.declare_queue(
            "seo-submit",
            durable=True
        )

        await queue.bind(
            exchange=exchange,
            routing_key="submit.created"
        )

        print("Submit Worker: Waiting for messages...")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body = message.body.decode()
                    try:
                        parsed_message = json.loads(body)
                        print(f"Received Submit Message: {parsed_message}")
                        await process_submit_job(parsed_message)
                    except Exception as e:
                        print(f"Error decoding/processing submit message: {e}")


def start_submit_consumer():
    asyncio.run(run_submit_consumer())