namespace SeoAudit.Domain.Entities;
public class SeoReport
{
    public Guid Id { get; set; }

    public Guid AuditJobId { get; set; }

    public int SeoScore { get; set; }

    public int TechnicalScore { get; set; }

    public int OnPageScore { get; set; }

    public DateTime CreatedAt { get; set; }
}