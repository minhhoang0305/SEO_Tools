using Microsoft.Extensions.Options;
using System.Security.Claims;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using SeoAudit.Application.Options;
using SeoAudit.Application.Feature.Auth.Interfaces;
namespace SeoAudit.Application.Feature.Auth.Service;
public class JwtService : IJwtService
{
    private readonly JwtOptions _options;
    public JwtService(IOptions<JwtOptions> options)
    {
        _options = options.Value;
    }
    public string GenerateToken(string? displayName, string email)
    {
        if (!JwtRsaKeyReader.HasPrivateKey(_options) || !JwtRsaKeyReader.CanCreatePrivateKey(_options))
            throw new InvalidOperationException("JWT private key is missing or invalid. Configure Jwt:PrivateKeyPem or Jwt:PrivateKeyBase64.");

        var securityKey = JwtRsaKeyReader.CreatePrivateKey(_options);
        var credentials = new SigningCredentials(securityKey, SecurityAlgorithms.RsaSha256);
        var claim = new[]
        {
            new Claim(ClaimTypes.Name, displayName ?? string.Empty),
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