using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
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

    public async Task<List<AuditJob>> GetListByUserIdAsync(
        Guid userId,
        CancellationToken cancellationToken = default)
    {
        return await dbContext.AuditJobs
            .Where(x => x.UserId == userId)
            .OrderByDescending(x => x.CreatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task<AuditJob?> GetByIdAsync(
        Guid id,
        CancellationToken cancellationToken = default)
    {
        return await dbContext.AuditJobs
            .FirstOrDefaultAsync(x => x.Id == id, cancellationToken);
    }

    public async Task<SeoReport?> GetReportByAuditJobIdAsync(
        Guid auditJobId,
        CancellationToken cancellationToken = default)
    {
        return await dbContext.SeoReports
            .FirstOrDefaultAsync(x => x.AuditJobId == auditJobId, cancellationToken);
    }

    public async Task<List<SeoIssue>> GetIssuesByReportIdAsync(
        Guid reportId,
        CancellationToken cancellationToken = default)
    {
        return await dbContext.SeoIssues
            .Where(x => x.ReportId == reportId)
            .ToListAsync(cancellationToken);
    }
}