using IdentityService.Domain.Models;
using IdentityService.Application.Contracts;
using IdentityService.Domain.Common;
namespace IdentityService.Domain.Interfaces;
public interface IRefreshService
{
    Task<Token> GenerateTokenAsync(User user);
    Task<Result<Token>> RefreshAsync(string refreshToken);
    Task<Result<string>> RevokeAsync(string refreshToken);
}
