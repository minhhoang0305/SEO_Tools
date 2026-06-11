using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using SeoAudit.Domain.Entities;
using SeoAudit.Domain.Interfaces;
using SeoAudit.Infrastructure.Persistence.Data;

namespace SeoAudit.Infrastructure.Repositories;

public class SubmitRepository(AppDbContext dbContext) : ISubmitRepository
{
    public async Task AddJobAsync(SubmitJob job, CancellationToken cancellationToken)
    {
        await dbContext.SubmitJobs.AddAsync(job, cancellationToken);
        await dbContext.SaveChangesAsync(cancellationToken);
    }

    public async Task<SubmitJob?> GetJobByIdAsync(Guid jobId, CancellationToken cancellationToken)
    {
        return await dbContext.SubmitJobs
            .Include(x => x.Details)
                .ThenInclude(d => d.Platform)
            .Include(x => x.Details)
                .ThenInclude(d => d.AuditLogs)
            .FirstOrDefaultAsync(x => x.Id == jobId, cancellationToken);
    }

    public async Task<List<SubmitJob>> GetJobsByUserIdAsync(Guid userId, CancellationToken cancellationToken)
    {
        return await dbContext.SubmitJobs
            .Include(x => x.Details)
                .ThenInclude(d => d.Platform)
            .Where(x => x.UserId == userId)
            .OrderByDescending(x => x.CreatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task<List<SeoPlatform>> GetActivePlatformsAsync(CancellationToken cancellationToken)
    {
        return await dbContext.SeoPlatforms
            .Where(x => x.IsActive)
            .OrderBy(x => x.Name)
            .ToListAsync(cancellationToken);
    }

    public async Task<PlatformCredential?> GetCredentialAsync(Guid userId, Guid platformId, CancellationToken cancellationToken)
    {
        return await dbContext.PlatformCredentials
            .FirstOrDefaultAsync(x => x.UserId == userId && x.PlatformId == platformId, cancellationToken);
    }

    public async Task SaveCredentialAsync(PlatformCredential credential, CancellationToken cancellationToken)
    {
        var existing = await dbContext.PlatformCredentials
            .FirstOrDefaultAsync(x => x.UserId == credential.UserId && x.PlatformId == credential.PlatformId, cancellationToken);

        if (existing == null)
        {
            await dbContext.PlatformCredentials.AddAsync(credential, cancellationToken);
        }
        else
        {
            existing.EncryptedData = credential.EncryptedData;
            existing.IV = credential.IV;
            existing.UpdatedAt = DateTime.UtcNow;
            dbContext.PlatformCredentials.Update(existing);
        }

        await dbContext.SaveChangesAsync(cancellationToken);
    }

    public async Task<SeoPlatform?> GetPlatformByCodeAsync(string code, CancellationToken cancellationToken)
    {
        return await dbContext.SeoPlatforms
            .FirstOrDefaultAsync(x => x.Code == code, cancellationToken);
    }

    public async Task<SeoPlatform?> GetPlatformByIdAsync(Guid platformId, CancellationToken cancellationToken)
    {
        return await dbContext.SeoPlatforms
            .FirstOrDefaultAsync(x => x.Id == platformId, cancellationToken);
    }
}
