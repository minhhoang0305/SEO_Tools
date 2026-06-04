using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using SeoAudit.Domain.Entities;

namespace SeoAudit.Infrastructure.Persistence.Configurations;

public class SeoIssueConfiguration : IEntityTypeConfiguration<SeoIssue>
{
    public void Configure(EntityTypeBuilder<SeoIssue> builder)
    {
        builder.ToTable("seo_issues");

        builder.HasKey(x => x.Id);

        builder.Property(x => x.ReportId)
            .IsRequired();

        builder.Property(x => x.Severity)
            .IsRequired()
            .HasMaxLength(50);

        builder.Property(x => x.Title)
            .IsRequired()
            .HasMaxLength(300);

        builder.Property(x => x.Description)
            .IsRequired()
            .HasMaxLength(4000);

        builder.Property(x => x.Recommendation)
            .HasMaxLength(4000);

        builder.HasIndex(x => x.ReportId);
        builder.HasIndex(x => x.Severity);
    }
}