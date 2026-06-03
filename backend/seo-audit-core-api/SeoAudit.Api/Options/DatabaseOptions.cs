using System.ComponentModel.DataAnnotations;

namespace SeoAudit.Api.Options;

public class DatabaseOptions
{
    public const string SectionName = "ConnectionStrings";

    [Required(AllowEmptyStrings = false)]
    public string DefaultConnection { get; set; } = string.Empty;
}
