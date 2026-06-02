using IdentityService.Domain.Models;

namespace IdentityService.Domain.Interfaces;

public interface IUserService
{
    Task<bool> EmailExistsAsync(string email);
    Task AddAsync(User user);
}