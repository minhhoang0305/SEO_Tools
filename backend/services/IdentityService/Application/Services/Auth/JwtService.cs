using IdentityService.Domain.Interfaces;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using Microsoft.IdentityModel.Tokens;
using IdentityService.Infrastructure.Options;
using Microsoft.Extensions.Options;

namespace IdentityService.Application.Services;

public class JwtService : IJwtService
{
    private readonly JwtOptions _options;
    public JwtService(IOptions<JwtOptions> options)
    {
        _options = options.Value;
    }
    public string GenerateToken(string name, string email)
    {
        var securityKey = JwtRsaKeyReader.CreatePrivateKey(_options);
        var credentials = new SigningCredentials(securityKey, SecurityAlgorithms.RsaSha256);
        var claim = new[]
        {
            new Claim(ClaimTypes.Name, name),
            new Claim(ClaimTypes.Email, email),
        };
        var token = new JwtSecurityToken(
            _options.Issuer,
            _options.Audience,
            claim,
            expires:
            DateTime.UtcNow.AddMinutes(_options.Expireminutes),
            signingCredentials: credentials
        );
        return new JwtSecurityTokenHandler().WriteToken(token);
    }
}