namespace SeoAudit.Application.FeatureContracts.Auth.;

public record UserResponse(
    Guid Id,
    string FirebaseUid,
    string Email,
    string? DisplayName,
    string? PhotoUrl,
    bool EmailVerified,
    DateTimeOffset? LastLoginAt
);