namespace SeoAudit.Application.Feature;
public record CreatedAudit(
    string Url,
    string Keyword,
    string Language,
    string Country
);