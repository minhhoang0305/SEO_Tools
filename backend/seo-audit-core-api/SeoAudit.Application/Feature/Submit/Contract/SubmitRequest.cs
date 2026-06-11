using System;
using System.Collections.Generic;

namespace SeoAudit.Application.Feature.Submit.Contract;

public class SaveCredentialRequest
{
    public Guid PlatformId { get; set; }
    public string CredentialData { get; set; } = string.Empty;
}

public class ConnectPlatformRequest
{
    public Guid PlatformId { get; set; }
}

public class CreateSubmitJobRequest
{
    public string WebsiteUrl { get; set; } = string.Empty;
    public List<Guid> PlatformIds { get; set; } = new();

    // Meta-data tùy chọn
    public string? SiteName { get; set; }
    public string? Description { get; set; }
    public string? Keywords { get; set; }
    public string? SitemapUrl { get; set; }
    public string? ContactEmail { get; set; }
}

public class SubmitJobProgressDto
{
    public Guid JobId { get; set; }
    public string WebsiteUrl { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
    public List<SubmitJobDetailProgressDto> Details { get; set; } = new();
}

public class SubmitJobDetailProgressDto
{
    public Guid DetailId { get; set; }
    public string PlatformName { get; set; } = string.Empty;
    public string PlatformCode { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public string? ErrorMessage { get; set; }
    public DateTime UpdatedAt { get; set; }
    public List<SubmitAuditLogDto> AuditLogs { get; set; } = new();
}

public class SubmitAuditLogDto
{
    public Guid Id { get; set; }
    public string Action { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public string? LogContent { get; set; }
    public int? DurationMs { get; set; }
    public DateTime Timestamp { get; set; }
}
