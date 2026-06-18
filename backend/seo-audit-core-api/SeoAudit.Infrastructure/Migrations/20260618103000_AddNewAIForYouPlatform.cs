using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace SeoAudit.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class AddNewAIForYouPlatform : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql("""
                INSERT INTO seo_platforms
                    ("Id", "Name", "Code", "WebsiteUrl", "SubmitMethod", "IsActive", "CreatedAt")
                VALUES
                    ('7b1a2c3d-4e5f-4a6b-8c9d-1e2f3a4b5c6d', 'New AI For You', 'newaiforyou', 'https://newaiforyou.com', 'UI_Automation', TRUE, NOW())
                ON CONFLICT ("Code") DO NOTHING;
            """);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql("""
                DELETE FROM seo_platforms
                WHERE "Code" = 'newaiforyou';
            """);
        }
    }
}
