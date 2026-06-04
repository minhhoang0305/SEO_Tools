using System.Collections.Generic;
using SeoAudit.Domain.Entities;
namespace SeoAudit.Application.Interfaces;
public interface IAuditRepository
{
    Task AddAsync(AuditJob auditJob, CancellationToken cancellationToken);
    Task<List<AuditJob>> GetListByUserIdAsync(Guid userId, CancellationToken cancellationToken = default);
    Task<AuditJob?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default);
    Task<SeoReport?> GetReportByAuditJobIdAsync(Guid auditJobId, CancellationToken cancellationToken = default);
    Task<List<SeoIssue>> GetIssuesByReportIdAsync(Guid reportId, CancellationToken cancellationToken = default);
}