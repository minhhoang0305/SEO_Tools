using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using SeoAudit.Domain.Entities;

namespace SeoAudit.Domain.Interfaces;

public interface ISubmitRepository
{
    Task AddJobAsync(SubmitJob job, CancellationToken cancellationToken);
    Task<SubmitJob?> GetJobByIdAsync(Guid jobId, CancellationToken cancellationToken);
    Task<List<SubmitJob>> GetJobsByUserIdAsync(Guid userId, CancellationToken cancellationToken);
    Task<List<SeoPlatform>> GetActivePlatformsAsync(CancellationToken cancellationToken);
    Task<PlatformCredential?> GetCredentialAsync(Guid userId, Guid platformId, CancellationToken cancellationToken);
    Task SaveCredentialAsync(PlatformCredential credential, CancellationToken cancellationToken);
    Task<SeoPlatform?> GetPlatformByCodeAsync(string code, CancellationToken cancellationToken);
    Task<SeoPlatform?> GetPlatformByIdAsync(Guid platformId, CancellationToken cancellationToken);
}
