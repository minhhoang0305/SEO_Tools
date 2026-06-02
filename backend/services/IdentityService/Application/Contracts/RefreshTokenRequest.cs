namespace IdentityService.Application.Contracts;
public class RefreshTokenRequest
{
    public string RefreshToken { get; set; } = string.Empty;
}