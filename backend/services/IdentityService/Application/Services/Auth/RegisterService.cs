using IdentityService.Application.Contracts;
using IdentityService.Domain.Enum;
using IdentityService.Domain.Interfaces;
using IdentityService.Domain.Models;
using System.Security.Cryptography;

namespace IdentityService.Application.Services;

public sealed class RegisterService
{
    private readonly IRegisterRepository _sessions;
    private readonly IUserService _users;
    private readonly IEmailSender _emailSender;

    public RegisterService(
        IRegisterRepository sessions,
        IUserService users,
        IEmailSender emailSender)
    {
        _sessions = sessions;
        _users = users;
        _emailSender = emailSender;
    }

    public async Task<Guid> StartEmailVerificationAsync(
        RegisterEmailRequest request,
        string appBaseUrl)
    {
        var email = request.Email.Trim().ToLowerInvariant();

        if (await _users.EmailExistsAsync(email))
            throw new InvalidOperationException("Email already exists.");

        var token = Convert.ToHexString(RandomNumberGenerator.GetBytes(32));

        var session = new Register
        {
            Email = email,
            VerificationToken = token,
            EmailVerified = false,
            ExpireAt = DateTimeOffset.UtcNow.AddMinutes(15)
        };

        await _sessions.AddAsync(session);

        var verificationLink = $"{appBaseUrl}/api/register/email/verify?token={token}";
        await _emailSender.SendVerificationEmailAsync(email, verificationLink);

        return session.Id;
    }

    public async Task<Guid> VerifyEmailAsync(string token)
    {
        var session = await _sessions.GetByTokenAsync(token);

        if (session is null)
            throw new InvalidOperationException("Invalid verification token.");

        if (session.ExpireAt < DateTimeOffset.UtcNow)
        {
            await _sessions.DeleteAsync(session.Id);
            throw new InvalidOperationException("Verification token expired.");
        }

        session.EmailVerified = true;
        await _sessions.UpdateAsync(session);

        return session.Id;
    }

    public async Task<Guid> CompleteRegistrationAsync(CompleteRequest request)
    {
        var session = await _sessions.GetByIdAsync(request.SessionId);

        if (session is null)
            throw new InvalidOperationException("Registration session not found.");

        if (!session.EmailVerified)
            throw new InvalidOperationException("Email is not verified.");

        if (session.ExpireAt < DateTimeOffset.UtcNow)
        {
            await _sessions.DeleteAsync(session.Id);
            throw new InvalidOperationException("Registration session expired.");
        }

        if (await _users.EmailExistsAsync(session.Email))
            throw new InvalidOperationException("Email already exists.");

        var user = new User
        {
            Id = Guid.NewGuid(),
            Name = request.Name.Trim(),
            Email = session.Email,
            Password = BCrypt.Net.BCrypt.HashPassword(request.Password),
            EmailVerified = true,
            Status = UserStatus.Active
        };

        await _users.AddAsync(user);
        await _sessions.DeleteAsync(session.Id);

        return user.Id;
    }
}
