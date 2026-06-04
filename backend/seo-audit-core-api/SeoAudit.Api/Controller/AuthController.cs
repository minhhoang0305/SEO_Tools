using FirebaseAdmin.Auth;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using SeoAudit.Application.Feature.Auth;
using SeoAudit.Application.Feature.Auth.Interfaces;
using SeoAudit.Domain.Entities;

namespace SeoAudit.Api.Controller;



[ApiController]
[Route("api/auth")]
public class AuthController(IAuthService authService, FirebaseAuth firebaseAuth, IRefreshService refreshService) : ControllerBase
{
    [Authorize]
    [HttpPost("session")]
    public async Task<ActionResult<AuthSessionResponse>> CreateSession(CancellationToken cancellationToken)
    {
        var firebaseUid = User.FindFirst("user_id")?.Value
            ?? User.FindFirst("sub")?.Value;

        if (string.IsNullOrWhiteSpace(firebaseUid))
        {
            return Unauthorized();
        }

        var authorization = Request.Headers.Authorization.ToString();

        if (!authorization.StartsWith("Bearer ", StringComparison.OrdinalIgnoreCase))
        {
            return Unauthorized();
        }

        var idToken = authorization["Bearer ".Length..].Trim();

        var firebaseToken = await firebaseAuth
            .VerifyIdTokenAsync(idToken, cancellationToken);

        var user = await authService.CreateOrUpdateSessionAsync(firebaseToken, cancellationToken);
        var token = await refreshService.GenerateTokenAsync(new User
        {
            Id = user.Id,
            FirebaseUid = user.FirebaseUid,
            Email = user.Email,
            DisplayName = user.DisplayName,
            PhotoUrl = user.PhotoUrl,
            EmailVerified = user.EmailVerified,
            LastLoginAt = user.LastLoginAt
        });

        return Ok(new AuthSessionResponse(user, token));
    }

    [HttpPost("refresh")]
    public async Task<IActionResult> Refresh([FromBody] RefreshRequest req)
    {
        var result = await refreshService.RefreshAsync(req.RefreshToken);
        if (!result.IsSuccess) return Unauthorized(result.Error);
        return Ok(result.Value);
    }

    [HttpPost("logout")]
    public async Task<IActionResult> Logout([FromBody] RefreshRequest req)
    {
        var result = await refreshService.RevokeAsync(req.RefreshToken);
        if (!result.IsSuccess) return BadRequest(result.Error);
        return Ok(new { message = "Đăng xuất thành công" });
    }

    [Authorize]
    [HttpGet("me")]
    public async Task<ActionResult<UserRequest>> Me(CancellationToken cancellationToken)
    {
        var firebaseUid = User.FindFirst("user_id")?.Value
            ?? User.FindFirst("sub")?.Value;

        if (string.IsNullOrWhiteSpace(firebaseUid))
        {
            return Unauthorized();
        }

        var user = await authService.GetCurrentUserAsync(firebaseUid, cancellationToken);

        if (user is null)
        {
            return NotFound();
        }

        return Ok(user);
    }
}