using Microsoft.AspNetCore.Mvc;
using SeoAudit.Application.Feature;
using SeoAudit.Application.Features;

namespace SeoAudit.Api.Controllers;

[ApiController]
[Route("api/audits")]
public class AuditController(
    CreateAuditService createAuditService)
    : ControllerBase
{
    [HttpPost]
    public async Task<IActionResult> Create(
        [FromBody] CreatedAudit request,
        CancellationToken cancellationToken)
    {
        var auditId = await createAuditService.Handle(
            request,
            cancellationToken);

        return Ok(new
        {
            AuditId = auditId
        });
    }
}
