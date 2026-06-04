using System.ComponentModel.DataAnnotations;

namespace SeoAudit.Application.Options;

public class DatabaseOptions
{
    public const string SectionName = "ConnectionStrings";

    [Required(AllowEmptyStrings = false)]
    public string DefaultConnection { get; set; } = string.Empty;
}
