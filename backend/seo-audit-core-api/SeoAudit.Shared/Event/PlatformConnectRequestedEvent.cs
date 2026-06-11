using System;

namespace SeoAudit.Shared;

public class PlatformConnectRequestedEvent
{
    public Guid RequestId { get; set; }
    public Guid UserId { get; set; }
    public Guid PlatformId { get; set; }
    public string PlatformCode { get; set; } = string.Empty;
    public string PlatformName { get; set; } = string.Empty;
}
