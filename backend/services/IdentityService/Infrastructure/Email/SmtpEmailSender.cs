using System.Net;
using System.Net.Mail;
using IdentityService.Domain.Interfaces;
using Microsoft.Extensions.Options;
using IdentityService.Infrastructure.Options;

namespace IdentityService.Infrastructure.Email;

public sealed class SmtpEmailSender : IEmailSender
{
    private readonly SmtpOptions _options;
    private readonly ILogger<SmtpEmailSender> _logger;

    public SmtpEmailSender(IOptions<SmtpOptions> options, ILogger<SmtpEmailSender> logger)
    {
        _options = options.Value;
        _logger = logger;
    }

    public async Task SendVerificationEmailAsync(string email, string verificationLink)
    {
        ValidateOptions();

        using var message = new MailMessage
        {
            From = new MailAddress(_options.FromEmail, _options.FromName),
            Subject = "Verify your SEO Tools account",
            Body = BuildVerificationEmailBody(verificationLink),
            IsBodyHtml = true
        };

        message.To.Add(email);

        using var client = new SmtpClient(_options.Host, _options.Port)
        {
            EnableSsl = _options.EnableSsl,
            Credentials = new NetworkCredential(_options.Username, _options.Password)
        };

        await client.SendMailAsync(message);
        _logger.LogInformation("Verification email sent to {Email}", email);
    }

    private void ValidateOptions()
    {
        if (string.IsNullOrWhiteSpace(_options.Host))
        {
            throw new InvalidOperationException("SMTP host is not configured.");
        }

        if (string.IsNullOrWhiteSpace(_options.Username))
        {
            throw new InvalidOperationException("SMTP username is not configured.");
        }

        if (string.IsNullOrWhiteSpace(_options.Password))
        {
            throw new InvalidOperationException("SMTP password is not configured.");
        }

        if (string.IsNullOrWhiteSpace(_options.FromEmail))
        {
            throw new InvalidOperationException("SMTP from email is not configured.");
        }
    }

    private static string BuildVerificationEmailBody(string verificationLink)
    {
        return $"""
            <p>Verify your email to continue registration.</p>
            <p><a href="{verificationLink}">Verify email</a></p>
            <p>If the button does not work, copy this link:</p>
            <p>{verificationLink}</p>
            """;
    }
}
