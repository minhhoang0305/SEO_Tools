import asyncpg
import uuid


class PostgresRepository:

    def __init__(self, connection_string):

        self.connection_string = connection_string

    async def get_connection(self):

        return await asyncpg.connect(
            self.connection_string
        )
    async def save_report(
        self,
        audit_id,
        score
    ):
        conn = await self.get_connection()
        report_id = uuid.uuid4()

        await conn.execute(
            """
            INSERT INTO seo_reports
            (
                "Id",
                "AuditJobId",
                "SeoScore",
                "TechnicalScore",
                "OnPageScore",
                "CreatedAt"
            )
            VALUES
            (
                $1,
                $2,
                $3,
                $4,
                $5,
                NOW()
            )
            """,
            report_id,
            uuid.UUID(audit_id) if isinstance(audit_id, str) else audit_id,
            score,
            score,
            0
        )

        await conn.close()
        return report_id

    async def save_issue(
        self,
        report_id,
        issue
    ):

        conn = await self.get_connection()

        await conn.execute(
            """
            INSERT INTO seo_issues
            (
                "Id",
                "ReportId",
                "Severity",
                "Title",
                "Description",
                "Recommendation"
            )
            VALUES
            (
                $1,
                $2,
                $3,
                $4,
                $5,
                $6
            )
            """,
            uuid.uuid4(),
            uuid.UUID(report_id) if isinstance(report_id, str) else report_id,
            issue["severity"],
            issue["title"],
            issue["description"],
            issue["recommendation"]
        )

        await conn.close()

    async def mark_completed(
        self,
        audit_id
    ):

        conn = await self.get_connection()

        await conn.execute(
            """
            UPDATE audit_jobs
            SET "Status" = 'Completed',
                "CompletedAt" = NOW()
            WHERE "Id" = $1
            """,
            uuid.UUID(audit_id) if isinstance(audit_id, str) else audit_id
        )

        await conn.close()