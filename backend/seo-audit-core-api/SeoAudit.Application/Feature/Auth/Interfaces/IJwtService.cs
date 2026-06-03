namespace SeoAudit.Application.Feature.Auth.Interfaces;
public interface IJwtService
{
    string GenerateToken(string? displayName, string email);
}