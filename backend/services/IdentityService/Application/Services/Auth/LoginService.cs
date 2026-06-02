using IdentityService.Domain.Interfaces;
using IdentityService.Domain.Common;
using IdentityService.Domain.Models;

namespace IdentityService.Application.Services;

public class LoginService : IAuthRepository
{
    private readonly IAuthRepository _authRepository;
    public LoginService(IAuthRepository authRepository)
    {
        _authRepository = authRepository;
    }
    public Task<Result<User>> LoginAsync(string email, string password)
    {
        return _authRepository.LoginAsync(email, password);
    }
}