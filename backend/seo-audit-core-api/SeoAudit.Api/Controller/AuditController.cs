using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using SeoAudit.Application.Feature;
using SeoAudit.Application.Features;
using SeoAudit.Application.Interfaces;
using SeoAudit.Domain.Interfaces;
using System;
using System.Threading;
using System.Threading.Tasks;

namespace SeoAudit.Api.Controllers;

[Authorize]
[ApiController]
[Route("api/audits")]
public class AuditController(
    CreateAuditService createAuditService,
    IAuditRepository auditRepository,
    IUserRepository userRepository)
    : ControllerBase
{
    [HttpPost]
    public async Task<IActionResult> Create(
        [FromBody] CreatedAudit request,
        CancellationToken cancellationToken)
    {
        var firebaseUid = User.FindFirst("user_id")?.Value
            ?? User.FindFirst("sub")?.Value;

        if (string.IsNullOrWhiteSpace(firebaseUid))
        {
            return Unauthorized();
        }

        var user = await userRepository.GetByFirebaseUidAsync(firebaseUid, cancellationToken);
        if (user is null)
        {
            return Unauthorized();
        }

        var auditId = await createAuditService.Handle(
            request,
            user.Id,
            cancellationToken);

        return Ok(new
        {
            AuditId = auditId
        });
    }

    [HttpGet]
    public async Task<IActionResult> GetList(CancellationToken cancellationToken)
    {
        var firebaseUid = User.FindFirst("user_id")?.Value
            ?? User.FindFirst("sub")?.Value;

        if (string.IsNullOrWhiteSpace(firebaseUid))
        {
            return Unauthorized();
        }

        var user = await userRepository.GetByFirebaseUidAsync(firebaseUid, cancellationToken);
        if (user is null)
        {
            return Unauthorized();
        }

        var audits = await auditRepository.GetListByUserIdAsync(user.Id, cancellationToken);

        return Ok(audits);
    }

    [HttpGet("{id:guid}")]
    public async Task<IActionResult> GetDetails(
        Guid id,
        CancellationToken cancellationToken)
    {
        var firebaseUid = User.FindFirst("user_id")?.Value
            ?? User.FindFirst("sub")?.Value;

        if (string.IsNullOrWhiteSpace(firebaseUid))
        {
            return Unauthorized();
        }

        var user = await userRepository.GetByFirebaseUidAsync(firebaseUid, cancellationToken);
        if (user is null)
        {
            return Unauthorized();
        }

        var audit = await auditRepository.GetByIdAsync(id, cancellationToken);
        if (audit is null || audit.UserId != user.Id)
        {
            return NotFound();
        }

        var report = await auditRepository.GetReportByAuditJobIdAsync(id, cancellationToken);
        object? reportData = null;

        if (report is not null)
        {
            var issues = await auditRepository.GetIssuesByReportIdAsync(report.Id, cancellationToken);
            reportData = new
            {
                report.Id,
                report.SeoScore,
                report.TechnicalScore,
                report.OnPageScore,
                report.CreatedAt,
                Issues = issues
            };
        }

        return Ok(new
        {
            audit.Id,
            audit.Url,
            audit.Keyword,
            audit.Language,
            audit.Country,
            Status = audit.Status.ToString(),
            audit.CreatedAt,
            audit.CompletedAt,
            Report = reportData
        });
    }
}
