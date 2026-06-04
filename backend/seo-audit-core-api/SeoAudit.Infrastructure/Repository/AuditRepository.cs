using Microsoft.EntityFrameworkCore;
using SeoAudit.Application.Interfaces;
using SeoAudit.Domain.Entities;
using SeoAudit.Infrastructure.Persistence.Data;

namespace SeoAudit.Infrastructure.Repositories;

public class AuditRepository(
    AppDbContext dbContext)
    : IAuditRepository
{
    public async Task AddAsync(
        AuditJob auditJob,
        CancellationToken cancellationToken = default)
    {
        await dbContext.AuditJobs.AddAsync(
            auditJob,
            cancellationToken);

        await dbContext.SaveChangesAsync(
            cancellationToken);
    }
}