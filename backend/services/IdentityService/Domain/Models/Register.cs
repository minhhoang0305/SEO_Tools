namespace IdentityService.Domain.Models;

public class Register
{
    public Guid Id {get; set;} = Guid.NewGuid();
    public string Email {get; set;} = string.Empty;
    public string VerificationToken {get; set;} =string.Empty;
    public bool EmailVerified {get; set;}
    public DateTimeOffset ExpireAt {get; set;}
    public DateTimeOffset CreatedAt {get; set;} = DateTimeOffset.UtcNow;

}