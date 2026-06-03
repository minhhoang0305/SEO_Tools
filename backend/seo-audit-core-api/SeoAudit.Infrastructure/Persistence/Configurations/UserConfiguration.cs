using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using SeoAudit.Domain.Entities;

namespace SeoAudit.Infrastructure.Persistence.Configurations;

public class UserConfiguration : IEntityTypeConfiguration<User>
{
    public void Configure(EntityTypeBuilder<User> builder)
    {
        builder.ToTable("app_users");
        builder.HasKey(x => x.Id);

        builder.Property(x => x.FirebaseUid)
            .IsRequired()
            .HasMaxLength(128);

        builder.HasIndex(x => x.FirebaseUid)
            .IsUnique();

        builder.Property(x => x.Email)
            .IsRequired()
            .HasMaxLength(320);

        builder.HasIndex(x => x.Email);

        builder.Property(x => x.DisplayName)
            .HasMaxLength(200);

        builder.Property(x => x.PhotoUrl)
            .HasMaxLength(1000);

        builder.Property(x => x.Provider)
            .HasMaxLength(100);

        builder.Property(x => x.CreatedAt)
            .IsRequired();

        builder.Property(x => x.UpdatedAt)
            .IsRequired();
    }
}
