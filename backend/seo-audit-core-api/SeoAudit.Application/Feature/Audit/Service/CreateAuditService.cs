using SeoAudit.Application.Feature;
using SeoAudit.Application.Interfaces;
using SeoAudit.Domain.Entities;
using SeoAudit.Domain.Enum;
using SeoAudit.Shared;

namespace SeoAudit.Application.Features;

public class CreateAuditService(
    IAuditRepository auditRepository,
    IMessagePublisher publisher)
{
    public async Task<Guid> Handle(
        CreatedAudit request,
        Guid userId,
        CancellationToken cancellationToken)
    {
        var audit = new AuditJob
        {
            Id = Guid.NewGuid(),
            UserId = userId,
            Url = request.Url,
            Keyword = request.Keyword,
            Language = request.Language,
            Country = request.Country,
            Status = AuditStatus.Pending,
            CreatedAt = DateTime.UtcNow
        };

        await auditRepository.AddAsync(
            audit,
            cancellationToken);

        var auditCreatedEvent = new AuditCreatedEvent
        {
            AuditId = audit.Id,
            Url = audit.Url,
            Keyword = audit.Keyword,
            Language = audit.Language,
            Country = audit.Country
        };

        await publisher.PublishAsync(
            "audit.created",
            auditCreatedEvent,
            cancellationToken);

        return audit.Id;
    }
}
