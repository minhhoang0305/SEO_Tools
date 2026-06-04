namespace SeoAudit.Shared;

public class AuditCreatedEvent
{
    public Guid AuditId { get; set; }

    public string Url { get; set; } = string.Empty;

    public string Keyword { get; set; } = string.Empty;

    public string Language { get; set; } = string.Empty;

    public string Country { get; set; } = string.Empty;
}