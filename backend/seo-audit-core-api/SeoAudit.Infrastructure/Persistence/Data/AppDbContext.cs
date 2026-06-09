using Microsoft.EntityFrameworkCore;
using SeoAudit.Domain.Entities;

namespace SeoAudit.Infrastructure.Persistence.Data;

public class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    public DbSet<User> User => Set<User>();
    public DbSet<AuditJob> AuditJobs => Set<AuditJob>();
    public DbSet<SeoReport> SeoReports => Set<SeoReport>();
    public DbSet<SeoIssue> SeoIssues => Set<SeoIssue>();
    public DbSet<SeoPlatform> SeoPlatforms => Set<SeoPlatform>();
    public DbSet<PlatformCredential> PlatformCredentials => Set<PlatformCredential>();
    public DbSet<SubmitJob> SubmitJobs => Set<SubmitJob>();
    public DbSet<SubmitJobDetail> SubmitJobDetails => Set<SubmitJobDetail>();
    public DbSet<SubmitAuditLog> SubmitAuditLogs => Set<SubmitAuditLog>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
    }
}
