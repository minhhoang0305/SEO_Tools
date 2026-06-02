namespace IdentityService.Domain.Interfaces;
public interface IJwtService
{
    string GenerateToken(string name, string email);
}