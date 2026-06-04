namespace SeoAudit.Application.Feature.Auth.Contracts;

public record UserResponse(
    Guid Id,
    string FirebaseUid,
    string Email,
    string? DisplayName,
    string? PhotoUrl,
    bool EmailVerified,
    DateTimeOffset? LastLoginAt
);