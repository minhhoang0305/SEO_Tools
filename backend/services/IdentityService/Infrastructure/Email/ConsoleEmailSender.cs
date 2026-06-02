using IdentityService.Domain.Interfaces;

namespace IdentityService.Infrastructure.Email;

public sealed class ConsoleEmailSender : IEmailSender
{
    private readonly ILogger<ConsoleEmailSender> _logger;

    public ConsoleEmailSender(ILogger<ConsoleEmailSender> logger)
    {
        _logger = logger;
    }

    public Task SendVerificationEmailAsync(string email, string verificationLink)
    {
        _logger.LogInformation("Verification email for {Email}: {VerificationLink}", email, verificationLink);
        return Task.CompletedTask;
    }
}