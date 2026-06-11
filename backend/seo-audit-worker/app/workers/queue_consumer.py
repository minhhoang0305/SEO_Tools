import json
import asyncio

from app.core.config import (
    RABBITMQ_HOST,
    RABBITMQ_QUEUE,
    DATABASE_URL
)

from app.engines.crawler import crawl
from app.engines.technical_seo import analyze_technical_seo
from app.engines.scoring import calculate
from app.repositories.postgres_repository import PostgresRepository
from app.engines.llm import generate_ai_seo_suggestions
from app.platforms.queue_processor import QueueJobProcessor
# from app.core.helper import print_seo_result


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
    print(seo_result)
    # print_seo_result(seo_result)

    score_result = calculate(
        seo_result,
        keyword=keyword,
        target_language=language
    )

    print("\nSEO Score")
    print(score_result)

    print("Đang lấy gợi ý tối ưu từ AI (Gemini)...")
    ai_result = await generate_ai_seo_suggestions(
        url=url,
        seo_result=seo_result,
        issues=score_result["issues"],
        keyword=keyword
    )
    if ai_result.get("success"):
        score_result = {
            "score": ai_result["score"],
            "technical_score": ai_result["technical_score"],
            "on_page_score": ai_result["on_page_score"],
            "issues": ai_result["issues"]
        }
        print("Đã tích hợp thành công kết quả chấm điểm và gợi ý từ AI!")
    else:
        print(f"Bỏ qua gợi ý AI do lỗi: {ai_result.get('error')}. Sử dụng kết quả tính toán tĩnh.")

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


async def handle_audit_error(message, exc: Exception):
    print(f"Error processing audit message: {exc}")
    if message and "AuditId" in message:
        audit_id = message["AuditId"]
        try:
            async with PostgresRepository(DATABASE_URL) as db_repo:
                await db_repo.mark_failed(audit_id)
            print(f"Successfully marked audit job {audit_id} as Failed in DB")
        except Exception as db_err:
            print(f"Failed to mark audit job {audit_id} as Failed in DB: {db_err}")


async def run_consumer():
    processor = QueueJobProcessor(
        host=RABBITMQ_HOST,
        exchange_name="audit.exchange",
        queue_name=RABBITMQ_QUEUE,
        routing_key="audit.created",
    )

    print("Waiting for messages...")

    await processor.run(process_audit, handle_audit_error)


def start_consumer():
    asyncio.run(run_consumer())
