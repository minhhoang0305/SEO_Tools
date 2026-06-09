using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace SeoAudit.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class AddSubmitWebsiteTables : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "seo_platforms",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    Name = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    Code = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    WebsiteUrl = table.Column<string>(type: "character varying(255)", maxLength: 255, nullable: true),
                    SubmitMethod = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    IsActive = table.Column<bool>(type: "boolean", nullable: false, defaultValue: true),
                    CreatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_seo_platforms", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "submit_jobs",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    UserId = table.Column<Guid>(type: "uuid", nullable: false),
                    WebsiteUrl = table.Column<string>(type: "character varying(2048)", maxLength: 2048, nullable: false),
                    Payload = table.Column<string>(type: "text", nullable: true),
                    Status = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    CompletedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_submit_jobs", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "platform_credentials",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    PlatformId = table.Column<Guid>(type: "uuid", nullable: false),
                    UserId = table.Column<Guid>(type: "uuid", nullable: false),
                    EncryptedData = table.Column<string>(type: "text", nullable: false),
                    IV = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_platform_credentials", x => x.Id);
                    table.ForeignKey(
                        name: "FK_platform_credentials_seo_platforms_PlatformId",
                        column: x => x.PlatformId,
                        principalTable: "seo_platforms",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "submit_job_details",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    JobId = table.Column<Guid>(type: "uuid", nullable: false),
                    PlatformId = table.Column<Guid>(type: "uuid", nullable: false),
                    Status = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    ErrorMessage = table.Column<string>(type: "text", nullable: true),
                    ResponseData = table.Column<string>(type: "text", nullable: true),
                    RetryCount = table.Column<int>(type: "integer", nullable: false, defaultValue: 0),
                    UpdatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_submit_job_details", x => x.Id);
                    table.ForeignKey(
                        name: "FK_submit_job_details_seo_platforms_PlatformId",
                        column: x => x.PlatformId,
                        principalTable: "seo_platforms",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_submit_job_details_submit_jobs_JobId",
                        column: x => x.JobId,
                        principalTable: "submit_jobs",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "submit_audit_logs",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    JobDetailId = table.Column<Guid>(type: "uuid", nullable: false),
                    Action = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    Status = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    LogContent = table.Column<string>(type: "text", nullable: true),
                    DurationMs = table.Column<int>(type: "integer", nullable: true),
                    Timestamp = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_submit_audit_logs", x => x.Id);
                    table.ForeignKey(
                        name: "FK_submit_audit_logs_submit_job_details_JobDetailId",
                        column: x => x.JobDetailId,
                        principalTable: "submit_job_details",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_platform_credentials_PlatformId",
                table: "platform_credentials",
                column: "PlatformId");

            migrationBuilder.CreateIndex(
                name: "IX_platform_credentials_UserId_PlatformId",
                table: "platform_credentials",
                columns: new[] { "UserId", "PlatformId" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_seo_platforms_Code",
                table: "seo_platforms",
                column: "Code",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_seo_platforms_Name",
                table: "seo_platforms",
                column: "Name",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_submit_audit_logs_JobDetailId",
                table: "submit_audit_logs",
                column: "JobDetailId");

            migrationBuilder.CreateIndex(
                name: "IX_submit_job_details_JobId",
                table: "submit_job_details",
                column: "JobId");

            migrationBuilder.CreateIndex(
                name: "IX_submit_job_details_PlatformId",
                table: "submit_job_details",
                column: "PlatformId");

            migrationBuilder.CreateIndex(
                name: "IX_submit_job_details_Status",
                table: "submit_job_details",
                column: "Status");

            migrationBuilder.CreateIndex(
                name: "IX_submit_jobs_Status",
                table: "submit_jobs",
                column: "Status");

            migrationBuilder.CreateIndex(
                name: "IX_submit_jobs_UserId",
                table: "submit_jobs",
                column: "UserId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "platform_credentials");

            migrationBuilder.DropTable(
                name: "submit_audit_logs");

            migrationBuilder.DropTable(
                name: "submit_job_details");

            migrationBuilder.DropTable(
                name: "seo_platforms");

            migrationBuilder.DropTable(
                name: "submit_jobs");
        }
    }
}
