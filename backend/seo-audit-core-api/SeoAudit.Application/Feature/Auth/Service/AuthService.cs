using FirebaseAdmin.Auth;
using System.Collections;
using SeoAudit.Application.Feature.Auth;
using SeoAudit.Application.Feature.Auth.Contracts;
using SeoAudit.Domain.Entities;
using SeoAudit.Domain.Interfaces;

namespace SeoAudit.Application.Feature.Auth.Service;

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
            throw new InvalidOperationException(
                "Firebase token does not contain an email.");
        }

        var displayName = firebaseToken.Claims.TryGetValue("name", out var nameClaim)
            ? nameClaim?.ToString()
            : null;

        var photoUrl = firebaseToken.Claims.TryGetValue("picture", out var pictureClaim)
            ? pictureClaim?.ToString()
            : null;

        var emailVerified =
            firebaseToken.Claims.TryGetValue("email_verified", out var verifiedClaim)
            && verifiedClaim is bool verified
            && verified;

        var provider = ExtractProvider(firebaseToken);

        var user = await userRepository.GetByFirebaseUidAsync(
            firebaseUid,
            cancellationToken);

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

            user = await userRepository.CreateAsync(
                user,
                cancellationToken);
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

            user = await userRepository.UpdateAsync(
                user,
                cancellationToken);
        }

        return ToRequest(user);
    }

    public async Task<UserResponse?> GetCurrentUserAsync(
        string firebaseUid,
        CancellationToken cancellationToken = default)
    {
        var user = await userRepository.GetByFirebaseUidAsync(
            firebaseUid,
            cancellationToken);

        return user is null
            ? null
            : ToResponse(user);
    }

    private static UserResponse ToResponse(User user)
    {
        return new UserResponse(
            user.Id,
            user.FirebaseUid,
            user.Email,
            user.DisplayName,
            user.PhotoUrl,
            user.EmailVerified,
            user.LastLoginAt
        );
    }

    private static UserRequest ToRequest(User user)
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

    private static string? ExtractProvider(FirebaseToken firebaseToken)
    {
        if (!firebaseToken.Claims.TryGetValue("firebase", out var firebaseClaim))
        {
            return null;
        }

        if (firebaseClaim is IReadOnlyDictionary<string, object> readOnlyDictionary &&
            readOnlyDictionary.TryGetValue("sign_in_provider", out var readOnlyProvider))
        {
            return readOnlyProvider?.ToString();
        }

        if (firebaseClaim is IDictionary<string, object> genericDictionary &&
            genericDictionary.TryGetValue("sign_in_provider", out var genericProvider))
        {
            return genericProvider?.ToString();
        }

        if (firebaseClaim is IDictionary firebaseDictionary &&
            firebaseDictionary.Contains("sign_in_provider"))
        {
            return firebaseDictionary["sign_in_provider"]?.ToString();
        }

        return firebaseClaim?.ToString() is { Length: <= 100 } provider
            ? provider
            : null;
    }
}