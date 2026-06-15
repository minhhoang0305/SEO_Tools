using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace SeoAudit.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class AddProductBurstPlatform : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql("""
                INSERT INTO seo_platforms
                    ("Id", "Name", "Code", "WebsiteUrl", "SubmitMethod", "IsActive", "CreatedAt")
                VALUES
                    ('c7f7d0b8-5d3c-4a56-9c69-9f2bf2e6d911', 'ProductBurst', 'productburst', 'https://productburst.com', 'UI_Automation', TRUE, NOW())
                ON CONFLICT ("Code") DO NOTHING;
            """);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql("""
                DELETE FROM seo_platforms
                WHERE "Code" = 'productburst';
            """);
        }
    }
}
