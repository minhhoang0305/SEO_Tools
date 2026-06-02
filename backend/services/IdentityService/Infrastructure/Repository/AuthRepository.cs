using IdentityService.Domain.Interfaces;
using IdentityService.Infrastructure.Persistence.Data;
using IdentityService.Domain.Common;
using IdentityService.Domain.Models;
namespace IdentityService.Infrastructure.Repository;

public class AuthRepository : IAuthRepository
{
    private readonly AppDbContext _context;

    public AuthRepository(AppDbContext context)
    {
        _context = context;
    }
    public Task<Result<User>> LoginAsync(string email, string password)
    {
        var user = _context.Users.FirstOrDefault(u => u.Email == email);
        if (user == null || !BCrypt.Net.BCrypt.Verify(password, user.Password))
        {
            return Task.FromResult(Result<User>.Failure(new Error("Auth.InvalidCredentials", "Email hoặc mật khẩu không đúng")));
        }
        return Task.FromResult(Result<User>.Success(user));
    }
}