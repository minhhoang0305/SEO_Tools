using SeoAudit.Domain.Models;

namespace SeoAudit.Application.Feature.Auth;

public sealed record AuthSessionResponse(
    UserRequest User,
    Token Token
);
