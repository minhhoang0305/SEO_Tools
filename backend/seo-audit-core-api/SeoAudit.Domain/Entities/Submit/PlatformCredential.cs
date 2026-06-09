using System;

namespace SeoAudit.Domain.Entities;

public class PlatformCredential
{
    public Guid Id { get; set; }
    public Guid PlatformId { get; set; }
    public Guid UserId { get; set; }
    public string EncryptedData { get; set; } = string.Empty;
    public string IV { get; set; } = string.Empty;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    public SeoPlatform? Platform { get; set; }
}
