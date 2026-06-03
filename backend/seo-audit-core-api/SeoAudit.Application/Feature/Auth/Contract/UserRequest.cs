namespace SeoAudit.Application.Feature.Auth;

public sealed record UserRequest(
    Guid Id,
    string FirebaseUid,
    string Email,
    string? DisplayName,
    string? PhotoUrl,
    bool EmailVerified,
    DateTimeOffset? LastLoginAt
);