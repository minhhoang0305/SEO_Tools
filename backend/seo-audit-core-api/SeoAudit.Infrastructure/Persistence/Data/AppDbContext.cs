using Microsoft.EntityFrameworkCore;
using SeoAudit.Domain.Entities;

namespace SeoAudit.Infrastructure.Persistence.Data;

public class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    public DbSet<User> User => Set<User>();
    public DbSet<AuditJob> AuditJobs => Set<AuditJob>();
    public DbSet<SeoReport> SeoReports => Set<SeoReport>();
    public DbSet<SeoIssue> SeoIssues => Set<SeoIssue>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
    }
}
