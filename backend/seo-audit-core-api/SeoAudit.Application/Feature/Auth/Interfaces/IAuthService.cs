using FirebaseAdmin.Auth;

namespace SeoAudit.Application.Feature.Auth;

public interface IAuthService
{
    Task<UserRequest> CreateOrUpdateSessionAsync(
        FirebaseToken firebaseToken,
        CancellationToken cancellationToken = default);

    Task<UserRequest?> GetCurrentUserAsync(
        string firebaseUid,
        CancellationToken cancellationToken = default);
}