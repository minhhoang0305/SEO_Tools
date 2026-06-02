namespace IdentityService.Application.Contracts;

public sealed record CompleteRequest(Guid SessionId, string Name, string Password);
