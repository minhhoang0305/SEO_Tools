using IdentityService.Domain.Models;
using IdentityService.Domain.Common;

namespace IdentityService.Domain.Interfaces;

public interface IAuthRepository
{
    public Task<Result<User>> LoginAsync(string email, string password);
}