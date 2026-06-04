using SeoAudit.Domain.Entities;
namespace SeoAudit.Application.Interfaces;
public interface IAuditRepository
{
    Task AddAsync(AuditJob auditJob, CancellationToken cancellationToken);
}