namespace SeoAudit.Domain.Entities;

public class User
{
    public Guid Id { get; set; }
    public string FirebaseUid { get; set; } = null!;
    public string Email { get; set; } = null!;
    public string? DisplayName { get; set; }
    public string? PhotoUrl { get; set; }
    public string? Provider { get; set; }
    public bool EmailVerified { get; set; }
    public bool IsActive { get; set; } = true;
    public DateTimeOffset? LastLoginAt { get; set; }
    public DateTimeOffset CreatedAt { get; set; }
    public DateTimeOffset UpdatedAt { get; set; }
}