using IdentityService.Domain.Enum;
namespace IdentityService.Domain.Models;

public class User
{
    public Guid Id {get; set;}
    public string Name {get; set;} = string.Empty;
    public string Email {get; set;} = string.Empty;
    public string Password {get; set;} = string.Empty;
    public bool EmailVerified {get; set;}
    public UserStatus Status {get; set;}
}