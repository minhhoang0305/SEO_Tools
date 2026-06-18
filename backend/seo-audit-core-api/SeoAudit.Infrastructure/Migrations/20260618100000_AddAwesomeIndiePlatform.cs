using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace SeoAudit.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class AddAwesomeIndiePlatform : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql("""
                INSERT INTO seo_platforms
                    ("Id", "Name", "Code", "WebsiteUrl", "SubmitMethod", "IsActive", "CreatedAt")
                VALUES
                    ('e7d3b6a2-2a77-4f7d-9e61-8cf1db3d1c23', 'Awesome Indie', 'awesome_indie', 'https://awesomeindie.com', 'UI_Automation', TRUE, NOW())
                ON CONFLICT ("Code") DO NOTHING;
            """);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql("""
                DELETE FROM seo_platforms
                WHERE "Code" = 'awesome_indie';
            """);
        }
    }
}
