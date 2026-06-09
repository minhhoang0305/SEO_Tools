using System;
using System.Collections.Generic;

namespace SeoAudit.Shared;

public class SubmitJobCreatedEvent
{
    public Guid JobId { get; set; }
    public string WebsiteUrl { get; set; } = string.Empty;
    public string? Payload { get; set; }
    public List<PlatformSubmitInfo> Platforms { get; set; } = new();
}

public class PlatformSubmitInfo
{
    public Guid JobDetailId { get; set; }
    public Guid PlatformId { get; set; }
    public string PlatformCode { get; set; } = string.Empty;
    public string SubmitMethod { get; set; } = string.Empty;
    public string? EncryptedCredential { get; set; }
    public string? IV { get; set; }
}
