using FirebaseAdmin.Auth;
using SeoAudit.Application.Feature.Auth.Contracts;

namespace SeoAudit.Application.Feature.Auth;

public interface IAuthService
{
    Task<UserRequest> CreateOrUpdateSessionAsync(
        FirebaseToken firebaseToken,
        CancellationToken cancellationToken = default);

    Task<UserResponse?> GetCurrentUserAsync(
        string firebaseUid,
        CancellationToken cancellationToken = default);
}