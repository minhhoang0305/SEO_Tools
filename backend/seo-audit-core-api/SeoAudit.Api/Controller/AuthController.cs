using FirebaseAdmin.Auth;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using SeoAudit.Application.Feature.Auth;

namespace SeoAudit.Api.Controller;

[ApiController]
[Route("api/auth")]
public class AuthController(IAuthService authService) : ControllerBase
{
    [Authorize]
    [HttpPost("session")]
    public async Task<ActionResult<UserRequest>> CreateSession(CancellationToken cancellationToken)
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

        var firebaseToken = await FirebaseAuth.DefaultInstance
            .VerifyIdTokenAsync(idToken, cancellationToken);

        var user = await authService.CreateOrUpdateSessionAsync(firebaseToken, cancellationToken);

        return Ok(user);
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