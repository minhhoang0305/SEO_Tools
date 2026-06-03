using System.ComponentModel.DataAnnotations;

namespace SeoAudit.Api.Options;

public class FirebaseOptions
{
    public const string SectionName = "Firebase";

    [Required(AllowEmptyStrings = false)]
    public string ProjectId { get; set; } = string.Empty;
}
