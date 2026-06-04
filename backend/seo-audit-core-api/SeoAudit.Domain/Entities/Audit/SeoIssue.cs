namespace SeoAudit.Domain.Entities;
public class SeoIssue
{
    public Guid Id { get; set; }

    public Guid ReportId { get; set; }

    public string Severity { get; set; } = string.Empty;

    public string Title { get; set; } = string.Empty;

    public string Description { get; set; } = string.Empty;

    public string Recommendation { get; set; } = string.Empty;
}