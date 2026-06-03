using FirebaseAdmin.Auth;
using SeoAudit.Domain.Entities;
using SeoAudit.Domain.Interfaces;

namespace SeoAudit.Application.Feature.Auth;

public class AuthService(IUserRepository userRepository) : IAuthService
{
    public async Task<UserRequest> CreateOrUpdateSessionAsync(
        FirebaseToken firebaseToken,
        CancellationToken cancellationToken = default)
    {
        var now = DateTimeOffset.UtcNow;
        var firebaseUid = firebaseToken.Uid;

        var email = firebaseToken.Claims.TryGetValue("email", out var emailClaim)
            ? emailClaim?.ToString()
            : null;

        if (string.IsNullOrWhiteSpace(email))
        {
            throw new InvalidOperationException("Firebase token does not contain an email.");
        }

        var displayName = firebaseToken.Claims.TryGetValue("name", out var nameClaim)
            ? nameClaim?.ToString()
            : null;

        var photoUrl = firebaseToken.Claims.TryGetValue("picture", out var pictureClaim)
            ? pictureClaim?.ToString()
            : null;

        var emailVerified = firebaseToken.Claims.TryGetValue("email_verified", out var verifiedClaim)
            && verifiedClaim is bool verified
            && verified;

        var provider = firebaseToken.Claims.TryGetValue("firebase", out var firebaseClaim)
            ? firebaseClaim?.ToString()
            : null;

        var user = await userRepository.GetByFirebaseUidAsync(firebaseUid, cancellationToken);

        if (user is null)
        {
            user = new User
            {
                Id = Guid.NewGuid(),
                FirebaseUid = firebaseUid,
                Email = email,
                DisplayName = displayName,
                PhotoUrl = photoUrl,
                Provider = provider,
                EmailVerified = emailVerified,
                LastLoginAt = now,
                CreatedAt = now,
                UpdatedAt = now
            };

            user = await userRepository.CreateAsync(user, cancellationToken);
        }
        else
        {
            user.Email = email;
            user.DisplayName = displayName;
            user.PhotoUrl = photoUrl;
            user.Provider = provider;
            user.EmailVerified = emailVerified;
            user.LastLoginAt = now;
            user.UpdatedAt = now;

            user = await userRepository.UpdateAsync(user, cancellationToken);
        }

        return ToDto(user);
    }

    public async Task<UserRequest?> GetCurrentUserAsync(
        string firebaseUid,
        CancellationToken cancellationToken = default)
    {
        var user = await userRepository.GetByFirebaseUidAsync(firebaseUid, cancellationToken);
        return user is null ? null : ToDto(user);
    }

    private static UserRequest ToDto(User user)
    {
        return new UserRequest(
            user.Id,
            user.FirebaseUid,
            user.Email,
            user.DisplayName,
            user.PhotoUrl,
            user.EmailVerified,
            user.LastLoginAt
        );
    }
}