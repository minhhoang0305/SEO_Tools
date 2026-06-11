using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using SeoAudit.Application.Feature.Submit.Contract;
using SeoAudit.Application.Features;
using SeoAudit.Domain.Interfaces;

namespace SeoAudit.Api.Controllers;

[Authorize]
[ApiController]
[Route("api/submit")]
public class SubmitController(
    SaveCredentialService saveCredentialService,
    CreateSubmitJobService createSubmitJobService,
    ISubmitRepository submitRepository,
    IUserRepository userRepository)
    : ControllerBase
{
    [HttpGet("platforms")]
    public async Task<IActionResult> GetPlatforms(CancellationToken cancellationToken)
    {
        var platforms = await submitRepository.GetActivePlatformsAsync(cancellationToken);
        return Ok(platforms.Select(p => new
        {
            p.Id,
            p.Name,
            p.Code,
            p.WebsiteUrl,
            p.SubmitMethod
        }));
    }

    [HttpPost("credentials")]
    public async Task<IActionResult> SaveCredential(
        [FromBody] SaveCredentialRequest request,
        CancellationToken cancellationToken)
    {
        var user = await GetCurrentUserAsync(cancellationToken);
        if (user == null) return Unauthorized();

        await saveCredentialService.Handle(request, user.Id, cancellationToken);
        return Ok(new { Message = "Lưu thông tin xác thực thành công." });
    }

    [HttpPost("platforms/connect")]
    public async Task<IActionResult> ConnectPlatform(
        [FromBody] ConnectPlatformRequest request,
        CancellationToken cancellationToken)
    {
        var user = await GetCurrentUserAsync(cancellationToken);
        if (user == null) return Unauthorized();

        return Accepted(new
        {
            Message = "Flow Connect đã chuyển sang local login. Hãy dùng Playwright local để xuất storage_state, sau đó import file JSON qua UI."
        });
    }

    [HttpPost("jobs")]
    public async Task<IActionResult> CreateJob(
        [FromBody] CreateSubmitJobRequest request,
        CancellationToken cancellationToken)
    {
        var user = await GetCurrentUserAsync(cancellationToken);
        if (user == null) return Unauthorized();

        try
        {
            var jobId = await createSubmitJobService.Handle(request, user.Id, cancellationToken);
            return Ok(new { JobId = jobId });
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(new { Message = ex.Message });
        }
    }

    [HttpGet("jobs/{id:guid}")]
    public async Task<IActionResult> GetJobDetails(
        Guid id,
        CancellationToken cancellationToken)
    {
        var user = await GetCurrentUserAsync(cancellationToken);
        if (user == null) return Unauthorized();

        var job = await submitRepository.GetJobByIdAsync(id, cancellationToken);
        if (job == null || job.UserId != user.Id)
        {
            return NotFound();
        }

        var dto = new SubmitJobProgressDto
        {
            JobId = job.Id,
            WebsiteUrl = job.WebsiteUrl,
            Status = job.Status.ToString(),
            CreatedAt = job.CreatedAt,
            CompletedAt = job.CompletedAt,
            Details = job.Details.Select(d => new SubmitJobDetailProgressDto
            {
                DetailId = d.Id,
                PlatformName = d.Platform?.Name ?? string.Empty,
                PlatformCode = d.Platform?.Code ?? string.Empty,
                Status = d.Status.ToString(),
                ErrorMessage = d.ErrorMessage,
                UpdatedAt = d.UpdatedAt,
                AuditLogs = d.AuditLogs.OrderBy(l => l.Timestamp).Select(l => new SubmitAuditLogDto
                {
                    Id = l.Id,
                    Action = l.Action,
                    Status = l.Status,
                    LogContent = l.LogContent,
                    DurationMs = l.DurationMs,
                    Timestamp = l.Timestamp
                }).ToList()
            }).ToList()
        };

        return Ok(dto);
    }

    [HttpGet("history")]
    public async Task<IActionResult> GetHistory(CancellationToken cancellationToken)
    {
        var user = await GetCurrentUserAsync(cancellationToken);
        if (user == null) return Unauthorized();

        var jobs = await submitRepository.GetJobsByUserIdAsync(user.Id, cancellationToken);
        
        var dtos = jobs.Select(job => new SubmitJobProgressDto
        {
            JobId = job.Id,
            WebsiteUrl = job.WebsiteUrl,
            Status = job.Status.ToString(),
            CreatedAt = job.CreatedAt,
            CompletedAt = job.CompletedAt,
            Details = job.Details.Select(d => new SubmitJobDetailProgressDto
            {
                DetailId = d.Id,
                PlatformName = d.Platform?.Name ?? string.Empty,
                PlatformCode = d.Platform?.Code ?? string.Empty,
                Status = d.Status.ToString(),
                ErrorMessage = d.ErrorMessage,
                UpdatedAt = d.UpdatedAt
            }).ToList()
        }).ToList();

        return Ok(dtos);
    }

    private async Task<Domain.Entities.User?> GetCurrentUserAsync(CancellationToken cancellationToken)
    {
        var firebaseUid = User.FindFirst("user_id")?.Value
            ?? User.FindFirst("sub")?.Value;

        if (string.IsNullOrWhiteSpace(firebaseUid))
        {
            return null;
        }

        return await userRepository.GetByFirebaseUidAsync(firebaseUid, cancellationToken);
    }
}
