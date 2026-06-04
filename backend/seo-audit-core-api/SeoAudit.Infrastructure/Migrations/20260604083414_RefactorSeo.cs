using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace SeoAudit.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class RefactorSeo : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "seo_issues",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    ReportId = table.Column<Guid>(type: "uuid", nullable: false),
                    Severity = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    Title = table.Column<string>(type: "character varying(300)", maxLength: 300, nullable: false),
                    Description = table.Column<string>(type: "character varying(4000)", maxLength: 4000, nullable: false),
                    Recommendation = table.Column<string>(type: "character varying(4000)", maxLength: 4000, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_seo_issues", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "seo_reports",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    AuditJobId = table.Column<Guid>(type: "uuid", nullable: false),
                    SeoScore = table.Column<int>(type: "integer", nullable: false),
                    TechnicalScore = table.Column<int>(type: "integer", nullable: false),
                    OnPageScore = table.Column<int>(type: "integer", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_seo_reports", x => x.Id);
                });

            migrationBuilder.CreateIndex(
                name: "IX_seo_issues_ReportId",
                table: "seo_issues",
                column: "ReportId");

            migrationBuilder.CreateIndex(
                name: "IX_seo_issues_Severity",
                table: "seo_issues",
                column: "Severity");

            migrationBuilder.CreateIndex(
                name: "IX_seo_reports_AuditJobId",
                table: "seo_reports",
                column: "AuditJobId",
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "seo_issues");

            migrationBuilder.DropTable(
                name: "seo_reports");
        }
    }
}
