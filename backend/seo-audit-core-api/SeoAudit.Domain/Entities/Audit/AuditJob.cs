using SeoAudit.Domain.Enum;
namespace SeoAudit.Domain.Entities;
public class AuditJob
{
    public Guid Id { get; set; }

    public Guid UserId { get; set; }

    public string Url { get; set; } = string.Empty;

    public string Keyword { get; set; } = string.Empty;

    public string Language { get; set; } = string.Empty;

    public string Country { get; set; } = string.Empty;

    public AuditStatus Status { get; set; }

    public DateTime CreatedAt { get; set; }

    public DateTime? CompletedAt { get; set; }
}