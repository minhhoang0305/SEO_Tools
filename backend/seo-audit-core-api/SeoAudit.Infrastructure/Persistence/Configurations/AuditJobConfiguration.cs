using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using SeoAudit.Domain.Entities;

namespace SeoAudit.Infrastructure.Persistence.Configurations;

public class AuditJobConfiguration : IEntityTypeConfiguration<AuditJob>
{
    public void Configure(EntityTypeBuilder<AuditJob> builder)
    {
        builder.ToTable("audit_jobs");
        builder.HasKey(x => x.Id);

        builder.Property(x => x.UserId)
            .IsRequired();

        builder.Property(x => x.Url)
            .IsRequired()
            .HasMaxLength(2048);

        builder.Property(x => x.Keyword)
            .IsRequired()
            .HasMaxLength(300);

        builder.Property(x => x.Language)
            .IsRequired()
            .HasMaxLength(20);

        builder.Property(x => x.Country)
            .IsRequired()
            .HasMaxLength(20);

        builder.Property(x => x.Status)
            .IsRequired()
            .HasConversion<string>()
            .HasMaxLength(50);

        builder.Property(x => x.CreatedAt)
            .IsRequired();

        builder.HasIndex(x => x.UserId);
        builder.HasIndex(x => x.Status);
    }
}
