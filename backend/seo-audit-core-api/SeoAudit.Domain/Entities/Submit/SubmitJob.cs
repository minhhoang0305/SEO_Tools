using System;
using System.Collections.Generic;
using SeoAudit.Domain.Enum;

namespace SeoAudit.Domain.Entities;

public class SubmitJob
{
    public Guid Id { get; set; }
    public Guid UserId { get; set; }
    public string WebsiteUrl { get; set; } = string.Empty;
    public string? Payload { get; set; }
    public SubmitStatus Status { get; set; } = SubmitStatus.Pending;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? CompletedAt { get; set; }

    // Navigation properties
    public ICollection<SubmitJobDetail> Details { get; set; } = new List<SubmitJobDetail>();
}
