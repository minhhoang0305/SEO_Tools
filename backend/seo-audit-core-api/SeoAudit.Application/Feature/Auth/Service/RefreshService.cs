using Microsoft.Extensions.Options;
using StackExchange.Redis;
using System.Text.Json;
using System.Security.Cryptography;
using SeoAudit.Domain.Entities;
using SeoAudit.Domain.Models;
using Microsoft.IdentityModel.Tokens;
using SeoAudit.Shared;
using SeoAudit.Application.Feature.Auth.Interfaces;
using SeoAudit.Application.Options;
namespace SeoAudit.Application.Feature.Auth.Service;
public class RefreshService : IRefreshService
{
    private const string RefreshTokenKeyPrefix = "refresh-token:";

    private readonly IDatabase _database;
    private readonly IJwtService _jwtService;
    private readonly JwtOptions _jwtOptions;

    public RefreshService(
        IConnectionMultiplexer redis,
        IJwtService jwtService,
        IOptions<JwtOptions> jwtOptions)
    {
        _database = redis.GetDatabase();
        _jwtService = jwtService;
        _jwtOptions = jwtOptions.Value;
    }

    public async Task<Token> GenerateTokenAsync(User user)
    {
        var userName = string.IsNullOrWhiteSpace(user.DisplayName)
            ? user.Email
            : user.DisplayName;
        var accessToken = _jwtService.GenerateToken(userName, user.Email);
        var refreshToken = GenerateRefreshToken();
        var expiresAt = DateTime.UtcNow.AddDays(_jwtOptions.RefreshTokenExpireDays);

        var tokenData = new RefreshToken
        {
            UserId = user.Id,
            Email = user.Email,
            Username = user.DisplayName ?? user.Email,
            CreatedAt = DateTime.UtcNow,
            ExpiresAt = expiresAt,
            Jti = Guid.NewGuid().ToString("N")
        };

        await StoreRefreshTokenAsync(refreshToken, tokenData, expiresAt);

        return new Token
        {
            AccessToken = accessToken,
            RefreshToken = refreshToken
        };
    }

    public async Task<Result<Token>> RefreshAsync(string refreshToken)
    {
        if (string.IsNullOrWhiteSpace(refreshToken))
        {
            return Result<Token>.Failure(
                new Error("RefreshToken.Missing", "Refresh token is required"));
        }

        var key = GetRefreshTokenKey(refreshToken);
        var tokenJson = await _database.StringGetAsync(key);

        if (!tokenJson.HasValue)
        {
            return Result<Token>.Failure(
                new Error("RefreshToken.Invalid", "Refresh token is invalid or expired"));
        }

        var tokenData = JsonSerializer.Deserialize<RefreshToken>(tokenJson.ToString());
        if (tokenData is null || tokenData.ExpiresAt <= DateTime.UtcNow)
        {
            await _database.KeyDeleteAsync(key);
            return Result<Token>.Failure(
                new Error("RefreshToken.Invalid", "Refresh token is invalid or expired"));
        }

        await _database.KeyDeleteAsync(key);

        var user = new User
        {
            Id = tokenData.UserId,
            Email = tokenData.Email,
            DisplayName = tokenData.Username
        };

        var newToken = await GenerateTokenAsync(user);

        return Result<Token>.Success(newToken);
    }

    public async Task<Result<string>> RevokeAsync(string refreshToken)
    {
        if (string.IsNullOrWhiteSpace(refreshToken))
        {
            return Result<string>.Failure(
                new Error("RefreshToken.Missing", "Refresh token is required"));
        }

        await _database.KeyDeleteAsync(GetRefreshTokenKey(refreshToken));

        return Result<string>.Success("Đăng xuất thành công");
    }

    private async Task StoreRefreshTokenAsync(
        string refreshToken,
        RefreshToken tokenData,
        DateTime expiresAt)
    {
        var ttl = expiresAt - DateTime.UtcNow;
        if (ttl <= TimeSpan.Zero)
            throw new InvalidOperationException("Refresh token expiry must be in the future.");

        var tokenJson = JsonSerializer.Serialize(tokenData);

        await _database.StringSetAsync(
            GetRefreshTokenKey(refreshToken),
            tokenJson,
            ttl);
    }

    private static string GenerateRefreshToken()
    {
        var randomBytes = RandomNumberGenerator.GetBytes(64);
        return Base64UrlEncoder.Encode(randomBytes);
    }

    private static string GetRefreshTokenKey(string refreshToken)
    {
        return $"{RefreshTokenKeyPrefix}{HashToken(refreshToken)}";
    }

    private static string HashToken(string refreshToken)
    {
        var tokenBytes = System.Text.Encoding.UTF8.GetBytes(refreshToken);
        var hashBytes = SHA256.HashData(tokenBytes);
        return Convert.ToHexString(hashBytes);
    }
}