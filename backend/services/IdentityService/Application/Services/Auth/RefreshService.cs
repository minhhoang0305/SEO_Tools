using IdentityService.Domain.Interfaces;
using IdentityService.Infrastructure.Options;
using Microsoft.Extensions.Options;
using IdentityService.Domain.Models;
using System.Security.Cryptography;
namespace IdentityService.Application.Services;

public class RefreshService : IRefreshService
{
    private readonly IJwtService _jwtService;
    private readonly JwtOptions _jwtOptions;
    public RefreshService(IJwtService jwtService, IOptions<JwtOptions> jwtOptions)
    {
        _jwtService = jwtService;
        _jwtOptions = jwtOptions.Value;
    }
    public Task<Token> GenerateTokenAsync(User user)
    {
        var accessToken = _jwtService.GenerateToken(user.Name, user.Email);
        var refreshToken = GenerateRefreshToken();
        var expireAt = DateTime.UtcNow.AddDays(_jwtOptions.RefreshTokenExpireDays);

        var tokenData = new RefreshToken
        {
            UserId = user.Id.GetHashCode(),
            Email = user.Email,
            Username = user.Name,
            CreatedAt = DateTime.UtcNow,
            ExpiresAt = expireAt,
            Jti = Guid.NewGuid().ToString("N")
        };
        var token = new Token
        {
            AccessToken = accessToken,
            RefreshToken = refreshToken
        };

        return Task.FromResult(token);
    }
    private static string GenerateRefreshToken()
    {
        var randomBytes = RandomNumberGenerator.GetBytes(64);
        return Convert.ToBase64String(randomBytes);
    }
}