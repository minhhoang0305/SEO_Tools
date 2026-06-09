using System;

namespace SeoAudit.Domain.Entities;

public class SubmitAuditLog
{
    public Guid Id { get; set; }
    public Guid JobDetailId { get; set; }
    public string Action { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public string? LogContent { get; set; }
    public int? DurationMs { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;

    // Navigation properties
    public SubmitJobDetail? JobDetail { get; set; }
}
