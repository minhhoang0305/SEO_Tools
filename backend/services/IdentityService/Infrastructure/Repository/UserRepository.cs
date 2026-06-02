using IdentityService.Domain.Interfaces;
using IdentityService.Domain.Models;
using IdentityService.Infrastructure.Persistence.Data;
using Microsoft.EntityFrameworkCore;

namespace IdentityService.Infrastructure.Repository;

public sealed class UserRepository : IUserService
{
    private readonly AppDbContext _dbContext;

    public UserRepository(AppDbContext dbContext)
    {
        _dbContext = dbContext;
    }

    public Task<bool> EmailExistsAsync(string email)
    {
        return _dbContext.Users.AnyAsync(user => user.Email == email);
    }

    public async Task AddAsync(User user)
    {
        _dbContext.Users.Add(user);
        await _dbContext.SaveChangesAsync();
    }
}
