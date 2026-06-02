using Microsoft.AspNetCore.Mvc;
using IdentityService.Application.Services;
using IdentityService.Application.Contracts;
using IdentityService.Domain.Common;
using IdentityService.Domain.Interfaces;

namespace IdentityService.Api.Controller;

[ApiController]
[Route("api/auth")]
public class AuthController : ControllerBase
{
    private readonly RegisterService _registerService;
    private readonly LoginService _loginService;
    private readonly IRefreshService _refeshService;
    private readonly IConfiguration _configuration;

    public AuthController(RegisterService registerService, LoginService loginService, IRefreshService refreshService, IConfiguration configuration)
    {
        _registerService = registerService;
        _loginService = loginService;
        _refeshService = refreshService;
        _configuration = configuration;
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

        var frontendUrl = _configuration["Frontend:RedirectUrl"] ?? "http://localhost:5173/register/complete";

        return Redirect($"{frontendUrl}?sessionId={sessionId}");
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

    [HttpPost("refresh")]
    public async Task<IActionResult> Refresh([FromBody] RefreshTokenRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.RefreshToken))
            return BadRequest("Refresh token không được để trống.");

        var result = await _refeshService.RefreshAsync(request.RefreshToken);
        if (result.IsFailure)
            return Unauthorized(result.Error);

        var token = result.Value!;
        return Ok(new
        {
            access_token = token.AccessToken,
            refresh_token = token.RefreshToken,
            message = "Làm mới token thành công"
        });
    }

    [HttpPost("revoke")]
    public async Task<IActionResult> Revoke([FromBody] RefreshTokenRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.RefreshToken))
            return BadRequest("Refresh token không được để trống.");

        var result = await _refeshService.RevokeAsync(request.RefreshToken);
        if (result.IsFailure)
            return BadRequest(result.Error);

        return Ok(new
        {
            message = "Thu hồi token thành công"
        });
    }
}
