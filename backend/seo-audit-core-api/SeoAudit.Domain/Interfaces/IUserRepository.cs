using SeoAudit.Domain.Entities;

namespace SeoAudit.Domain.Interfaces;

public interface IUserRepository
{
    Task<User?> GetByFirebaseUidAsync(string firebaseUid, CancellationToken cancellationToken = default);

    Task<User> CreateAsync(User user, CancellationToken cancellationToken = default);

    Task<User> UpdateAsync(User user, CancellationToken cancellationToken = default);
}