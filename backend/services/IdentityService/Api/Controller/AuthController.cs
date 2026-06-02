using Microsoft.AspNetCore.Mvc;
using IdentityService.Application.Services;
using IdentityService.Application.Contracts;
using IdentityService.Domain.Common;

namespace IdentityService.Api.Controller;

[ApiController]
[Route("api/auth")]
public class AuthController : ControllerBase
{
    private readonly RegisterService _registerService;
    private readonly LoginService _loginService;
    private readonly RefreshService _refeshService;

    public AuthController(RegisterService registerService, LoginService loginService, JwtService jwtService, RefreshService refreshService)
    {
        _registerService = registerService;
        _loginService = loginService;
        _refeshService = refreshService;
    }

    [HttpPost("register")]
    public async Task<IActionResult> Register([FromBody] RegisterEmailRequest request)
    {
        var baseUrl = $"{Request.Scheme}://{Request.Host}";
        var sessionId = await _registerService.StartEmailVerificationAsync(request, baseUrl);

        return Ok(new
        {
            sessionId,
            message = "Verification email sent."
        });
    }

    [HttpGet("register/email/verify")]
    public async Task<IActionResult> VerifyEmail([FromQuery] string token)
    {
        var sessionId = await _registerService.VerifyEmailAsync(token);

        return Ok(new
        {
            sessionId,
            message = "Email verified. Continue registration with this sessionId."
        });
    }

    [HttpPost("register/complete")]
    public async Task<IActionResult> CompleteRegistration([FromBody] CompleteRequest request)
    {
        var userId = await _registerService.CompleteRegistrationAsync(request);

        return Ok(new
        {
            userId,
            message = "Registration completed."
        });
    }

    [HttpPost("login")]
    public async Task<IActionResult> Login([FromBody] LoginRequest request)
    {
        var result = await _loginService.LoginAsync(request.Email, request.Password); 
        if (result.IsFailure)
            return Unauthorized(result.Error);
        var user = result.Value!;
        var token = await _refeshService.GenerateTokenAsync(user);
        return Ok(new
        {
            access_token = token.AccessToken,
            refresh_token = token.RefreshToken,
            message = "Đăng kí thành công"
        });
    }
}