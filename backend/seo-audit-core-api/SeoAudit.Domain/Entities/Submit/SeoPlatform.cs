using System;

namespace SeoAudit.Domain.Entities;

public class SeoPlatform
{
    public Guid Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Code { get; set; } = string.Empty;
    public string? WebsiteUrl { get; set; }
    public string SubmitMethod { get; set; } = string.Empty; // e.g. "API", "UI_Automation"
    public bool IsActive { get; set; } = true;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
