import json
import asyncio

import pika

from app.core.config import (
    RABBITMQ_HOST,
    RABBITMQ_QUEUE,
    DATABASE_URL
)

from app.engines.crawler import crawl
from app.engines.technical_seo import analyze
from app.engines.scoring import calculate
from app.repositories.postgres_repository import PostgresRepository


async def process_audit(message):
    url = message["Url"]
    audit_id = message["AuditId"]

    crawl_result = await crawl(url)

    print(
        f"Status: {crawl_result['status_code']}"
    )

    print(
        f"HTML Length: {len(crawl_result['html'])}"
    )

    seo_result = analyze(
        crawl_result["html"],
        crawl_result["final_url"]
    )

    print("\nSEO Analysis")
    print(seo_result)

    score_result = calculate(
        seo_result
    )

    print("\nSEO Score")
    print(score_result)

    db_repo = PostgresRepository(DATABASE_URL)
    report_id = await db_repo.save_report(audit_id, score_result["score"])

    for issue in score_result["issues"]:
        await db_repo.save_issue(report_id, issue)

    await db_repo.mark_completed(audit_id)
    print(f"Successfully processed and saved audit for job {audit_id}")


def callback(
    ch,
    method,
    properties,
    body
):

    message = json.loads(
        body.decode()
    )

    print(
        f"Received Audit: {message}"
    )

    asyncio.run(process_audit(message))

    ch.basic_ack(
        delivery_tag=method.delivery_tag
    )

def start_consumer():

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST
        )
    )

    channel = connection.channel()

    channel.exchange_declare(
    exchange="audit.exchange",
    exchange_type="topic",
    durable=True
    )

    channel.queue_declare(
        queue="audit.queue",
        durable=True
    )

    channel.queue_bind(
        exchange="audit.exchange",
        queue="audit.queue",
        routing_key="audit.created"
    )

    channel.basic_qos(
    prefetch_count=1
    )

    channel.basic_consume(
    queue="audit.queue",
    on_message_callback=callback
    )

    print(
        "Waiting for messages..."
    )

    channel.start_consuming()