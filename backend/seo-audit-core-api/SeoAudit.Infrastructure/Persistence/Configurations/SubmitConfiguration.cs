using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using SeoAudit.Domain.Entities;

namespace SeoAudit.Infrastructure.Persistence.Configurations;

public class SeoPlatformConfiguration : IEntityTypeConfiguration<SeoPlatform>
{
    public void Configure(EntityTypeBuilder<SeoPlatform> builder)
    {
        builder.ToTable("seo_platforms");
        builder.HasKey(x => x.Id);

        builder.Property(x => x.Name)
            .IsRequired()
            .HasMaxLength(100);

        builder.Property(x => x.Code)
            .IsRequired()
            .HasMaxLength(50);

        builder.Property(x => x.WebsiteUrl)
            .HasMaxLength(255);

        builder.Property(x => x.SubmitMethod)
            .IsRequired()
            .HasMaxLength(50);

        builder.Property(x => x.IsActive)
            .HasDefaultValue(true);

        builder.Property(x => x.CreatedAt)
            .IsRequired();

        builder.HasIndex(x => x.Name).IsUnique();
        builder.HasIndex(x => x.Code).IsUnique();
    }
}

public class PlatformCredentialConfiguration : IEntityTypeConfiguration<PlatformCredential>
{
    public void Configure(EntityTypeBuilder<PlatformCredential> builder)
    {
        builder.ToTable("platform_credentials");
        builder.HasKey(x => x.Id);

        builder.Property(x => x.PlatformId)
            .IsRequired();

        builder.Property(x => x.UserId)
            .IsRequired();

        builder.Property(x => x.EncryptedData)
            .IsRequired();

        builder.Property(x => x.IV)
            .IsRequired()
            .HasMaxLength(100);

        builder.Property(x => x.UpdatedAt)
            .IsRequired();

        builder.HasOne(x => x.Platform)
            .WithMany()
            .HasForeignKey(x => x.PlatformId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasIndex(x => new { x.UserId, x.PlatformId }).IsUnique();
    }
}

public class SubmitJobConfiguration : IEntityTypeConfiguration<SubmitJob>
{
    public void Configure(EntityTypeBuilder<SubmitJob> builder)
    {
        builder.ToTable("submit_jobs");
        builder.HasKey(x => x.Id);

        builder.Property(x => x.UserId)
            .IsRequired();

        builder.Property(x => x.WebsiteUrl)
            .IsRequired()
            .HasMaxLength(2048);

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

public class SubmitJobDetailConfiguration : IEntityTypeConfiguration<SubmitJobDetail>
{
    public void Configure(EntityTypeBuilder<SubmitJobDetail> builder)
    {
        builder.ToTable("submit_job_details");
        builder.HasKey(x => x.Id);

        builder.Property(x => x.JobId)
            .IsRequired();

        builder.Property(x => x.PlatformId)
            .IsRequired();

        builder.Property(x => x.Status)
            .IsRequired()
            .HasConversion<string>()
            .HasMaxLength(50);

        builder.Property(x => x.RetryCount)
            .HasDefaultValue(0);

        builder.Property(x => x.UpdatedAt)
            .IsRequired();

        builder.HasOne(x => x.Job)
            .WithMany(j => j.Details)
            .HasForeignKey(x => x.JobId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasOne(x => x.Platform)
            .WithMany()
            .HasForeignKey(x => x.PlatformId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasIndex(x => x.JobId);
        builder.HasIndex(x => x.PlatformId);
        builder.HasIndex(x => x.Status);
    }
}

public class SubmitAuditLogConfiguration : IEntityTypeConfiguration<SubmitAuditLog>
{
    public void Configure(EntityTypeBuilder<SubmitAuditLog> builder)
    {
        builder.ToTable("submit_audit_logs");
        builder.HasKey(x => x.Id);

        builder.Property(x => x.JobDetailId)
            .IsRequired();

        builder.Property(x => x.Action)
            .IsRequired()
            .HasMaxLength(100);

        builder.Property(x => x.Status)
            .IsRequired()
            .HasMaxLength(50);

        builder.Property(x => x.Timestamp)
            .IsRequired();

        builder.HasOne(x => x.JobDetail)
            .WithMany(d => d.AuditLogs)
            .HasForeignKey(x => x.JobDetailId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasIndex(x => x.JobDetailId);
    }
}
