import json
import asyncio

import pika

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

    crawl_result = await crawl(url)

    print(
        f"Status: {crawl_result['status_code']}"
    )

    print(
        f"HTML Length: {len(crawl_result['html'])}"
    )

    seo_result = await analyze_technical_seo(
        crawl_result
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
    message = None
    try:
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
    except Exception as e:
        print(f"Error processing audit message: {e}")

        if message and "AuditId" in message:
            audit_id = message["AuditId"]
            try:
                db_repo = PostgresRepository(DATABASE_URL)
                asyncio.run(db_repo.mark_failed(audit_id))
                print(f"Successfully marked audit job {audit_id} as Failed in DB")
            except Exception as db_err:
                print(f"Failed to mark audit job {audit_id} as Failed in DB: {db_err}")

        try:
            ch.basic_ack(
                delivery_tag=method.delivery_tag
            )
        except Exception as ack_err:
            print(f"Failed to ack message after error: {ack_err}")


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

    channel.basic_consume(
        queue="audit.queue",
        on_message_callback=callback
    )

    print(
        "Waiting for messages..."
    )

    channel.start_consuming()