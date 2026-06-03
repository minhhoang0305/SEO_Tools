using Microsoft.EntityFrameworkCore;
using SeoAudit.Domain.Entities;
using SeoAudit.Domain.Interfaces;
using SeoAudit.Infrastructure.Persistence.Data;

namespace SeoAudit.Infrastructure.Repository;

public class UserRepository(AppDbContext dbContext) : IUserRepository
{
    public Task<User?> GetByFirebaseUidAsync(
        string firebaseUid,
        CancellationToken cancellationToken = default)
    {
        return dbContext.User
            .FirstOrDefaultAsync(x => x.FirebaseUid == firebaseUid, cancellationToken);
    }

    public async Task<User> CreateAsync(User user, CancellationToken cancellationToken = default)
    {
        dbContext.User.Add(user);
        await dbContext.SaveChangesAsync(cancellationToken);
        return user;
    }

    public async Task<User> UpdateAsync(User user, CancellationToken cancellationToken = default)
    {
        dbContext.User.Update(user);
        await dbContext.SaveChangesAsync(cancellationToken);
        return user;
    }
}