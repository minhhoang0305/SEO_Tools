namespace IdentityService.Domain.Interfaces;

public interface IEmailSender
{
    Task SendVerificationEmailAsync(string email, string verificationLink);
}