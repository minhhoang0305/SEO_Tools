using System;
using System.Collections.Generic;
using SeoAudit.Domain.Enum;

namespace SeoAudit.Domain.Entities;

public class SubmitJobDetail
{
    public Guid Id { get; set; }
    public Guid JobId { get; set; }
    public Guid PlatformId { get; set; }
    public SubmitStatus Status { get; set; } = SubmitStatus.Pending;
    public string? ErrorMessage { get; set; }
    public string? ResponseData { get; set; }
    public int RetryCount { get; set; } = 0;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    public SubmitJob? Job { get; set; }
    public SeoPlatform? Platform { get; set; }
    public ICollection<SubmitAuditLog> AuditLogs { get; set; } = new List<SubmitAuditLog>();
}
