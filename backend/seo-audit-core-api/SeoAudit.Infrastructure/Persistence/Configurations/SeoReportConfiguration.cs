using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using SeoAudit.Domain.Entities;

namespace SeoAudit.Infrastructure.Persistence.Configurations;

public class SeoReportConfiguration : IEntityTypeConfiguration<SeoReport>
{
    public void Configure(EntityTypeBuilder<SeoReport> builder)
    {
        builder.ToTable("seo_reports");

        builder.HasKey(x => x.Id);

        builder.Property(x => x.AuditJobId)
            .IsRequired();

        builder.Property(x => x.SeoScore)
            .IsRequired();

        builder.Property(x => x.TechnicalScore)
            .IsRequired();

        builder.Property(x => x.OnPageScore)
            .IsRequired();

        builder.Property(x => x.CreatedAt)
            .IsRequired();

        builder.HasIndex(x => x.AuditJobId);

        builder.HasIndex(x => x.AuditJobId)
            .IsUnique();
    }
}