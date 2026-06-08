import json
import asyncio

import aio_pika

from app.core.config import (
    RABBITMQ_HOST,
    RABBITMQ_QUEUE,
    DATABASE_URL
)

from app.engines.crawler import crawl
from app.engines.technical_seo import analyze_technical_seo
from app.engines.scoring import calculate
from app.repositories.postgres_repository import PostgresRepository


async def process_audit(message):
    url = message["Url"]
    audit_id = message["AuditId"]
    keyword = message.get("Keyword", "")
    language = message.get("Language", "")
    country = message.get("Country", "")

    crawl_result = await crawl(url, language=language, country=country)

    print(
        f"Status: {crawl_result['status_code']}"
    )

    print(
        f"HTML Length: {len(crawl_result['html'])}"
    )

    seo_result = await analyze_technical_seo(
        crawl_result,
        target_language=language
    )

    print("\nSEO Analysis")
    print(seo_result)

    score_result = calculate(
        seo_result,
        keyword=keyword,
        target_language=language
    )

    print("\nSEO Score")
    print(score_result)

    async with PostgresRepository(DATABASE_URL) as db_repo:
        report_id = await db_repo.save_report(
            audit_id,
            score_result["score"],
            score_result["technical_score"],
            score_result["on_page_score"]
        )

        await db_repo.save_issues(report_id, score_result["issues"])

        await db_repo.mark_completed(audit_id)
    print(f"Successfully processed and saved audit for job {audit_id}")


async def run_consumer():
    connection = await aio_pika.connect_robust(
        host=RABBITMQ_HOST
    )

    async with connection:
        channel = await connection.channel()

        await channel.declare_exchange(
            "audit.exchange",
            type=aio_pika.ExchangeType.TOPIC,
            durable=True
        )

        queue = await channel.declare_queue(
            RABBITMQ_QUEUE,
            durable=True
        )

        await queue.bind(
            exchange="audit.exchange",
            routing_key="audit.created"
        )

        print("Waiting for messages...")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body = message.body.decode()
                    parsed_message = None
                    try:
                        parsed_message = json.loads(body)
                        print(f"Received Audit: {parsed_message}")
                        await process_audit(parsed_message)
                    except Exception as e:
                        print(f"Error processing audit message: {e}")
                        if parsed_message and "AuditId" in parsed_message:
                            audit_id = parsed_message["AuditId"]
                            try:
                                async with PostgresRepository(DATABASE_URL) as db_repo:
                                    await db_repo.mark_failed(audit_id)
                                print(f"Successfully marked audit job {audit_id} as Failed in DB")
                            except Exception as db_err:
                                print(f"Failed to mark audit job {audit_id} as Failed in DB: {db_err}")


def start_consumer():
    asyncio.run(run_consumer())