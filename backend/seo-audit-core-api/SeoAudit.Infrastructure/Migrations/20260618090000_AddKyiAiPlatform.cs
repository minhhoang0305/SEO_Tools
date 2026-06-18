using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace SeoAudit.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class AddKyiAiPlatform : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql("""
                INSERT INTO seo_platforms
                    ("Id", "Name", "Code", "WebsiteUrl", "SubmitMethod", "IsActive", "CreatedAt")
                VALUES
                    ('c2f9c6d0-8e5c-4e0b-a5d8-5a7d4f0ef2b1', 'Kyi AI', 'kyi_ai', 'https://kyi.ai', 'UI_Automation', TRUE, NOW())
                ON CONFLICT ("Code") DO NOTHING;
            """);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql("""
                DELETE FROM seo_platforms
                WHERE "Code" = 'kyi_ai';
            """);
        }
    }
}
