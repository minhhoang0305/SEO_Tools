# pyrefly: ignore [missing-import]
import asyncpg
import uuid


class PostgresRepository:

    def __init__(self, connection_string):

        self.connection_string = connection_string
        self._conn = None

    async def __aenter__(self):
        self._conn = await asyncpg.connect(self.connection_string)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def get_connection(self):
        if self._conn:
            return self._conn
        return await asyncpg.connect(
            self.connection_string
        )

    async def close_connection(self, conn):
        if self._conn is None:
            await conn.close()

    async def save_report(
        self,
        audit_id,
        seo_score,
        technical_score,
        on_page_score
    ):
        conn = await self.get_connection()
        report_id = uuid.uuid4()
        audit_uuid = uuid.UUID(audit_id) if isinstance(audit_id, str) else audit_id

        async with conn.transaction():
            await conn.execute(
                """
                DELETE FROM seo_issues
                WHERE "ReportId" IN (
                    SELECT "Id" FROM seo_reports WHERE "AuditJobId" = $1
                )
                """,
                audit_uuid
            )
            await conn.execute(
                """
                DELETE FROM seo_reports
                WHERE "AuditJobId" = $1
                """,
                audit_uuid
            )
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
                audit_uuid,
                seo_score,
                technical_score,
                on_page_score
            )

        await self.close_connection(conn)
        return report_id

    async def save_issues(
        self,
        report_id,
        issues
    ):
        if not issues:
            return

        conn = await self.get_connection()
        report_uuid = uuid.UUID(report_id) if isinstance(report_id, str) else report_id

        data = [
            (
                uuid.uuid4(),
                report_uuid,
                issue["severity"],
                issue["title"],
                issue.get("description", ""),
                issue.get("recommendation", "")
            )
            for issue in issues
        ]

        async with conn.transaction():
            await conn.executemany(
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
                ($1, $2, $3, $4, $5, $6)
                """,
                data
            )

        await self.close_connection(conn)

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

        await self.close_connection(conn)

    async def mark_failed(
        self,
        audit_id
    ):

        conn = await self.get_connection()

        await conn.execute(
            """
            UPDATE audit_jobs
            SET "Status" = 'Failed',
                "CompletedAt" = NOW()
            WHERE "Id" = $1
            """,
            uuid.UUID(audit_id) if isinstance(audit_id, str) else audit_id
        )

        await self.close_connection(conn)