using SeoAudit.Domain.Entities;
using SeoAudit.Domain.Models;
using SeoAudit.Shared;
namespace SeoAudit.Application.Feature.Auth.Interfaces;
public interface IRefreshService
{
    Task<Token> GenerateTokenAsync(User user);
    Task<Result<Token>> RefreshAsync(string refreshToken);
    Task<Result<string>> RevokeAsync(string refreshToken);
}