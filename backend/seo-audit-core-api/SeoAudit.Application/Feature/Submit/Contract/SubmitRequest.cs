using System;
using System.Collections.Generic;

namespace SeoAudit.Application.Feature.Submit.Contract;

public class SaveCredentialRequest
{
    public Guid PlatformId { get; set; }
    public string CredentialData { get; set; } = string.Empty;
}

public class ConnectPlatformRequest
{
    public Guid PlatformId { get; set; }
}

public class CreateSubmitJobRequest
{
    public string WebsiteUrl { get; set; } = string.Empty;
    public List<Guid> PlatformIds { get; set; } = new();

    // Meta-data tùy chọn
    public string? SiteName { get; set; }
    public string? Tagline { get; set; }
    public string? Description { get; set; }
    public string? ProductDescription { get; set; }
    public string? Keywords { get; set; }
    public string? Categories { get; set; }
    public string? Category { get; set; }
    public string? Stacks { get; set; }
    public string? ProductType { get; set; }
    public string? LaunchPlan { get; set; }
    public string? LaunchWeek { get; set; }
    public string? SitemapUrl { get; set; }
    public string? ContactEmail { get; set; }
    public string? YourName { get; set; }
    public string? Pricing { get; set; }
    public string? NewsletterOptIn { get; set; }
    public string? TwitterHandle { get; set; }
    public string? TenWordsCategory { get; set; }
    public string? TenWordsNewsletter { get; set; }
    public bool? BAIToolsUseApi { get; set; }
    public int? BAIToolsPlanIndex { get; set; }
    public string? BAIToolsLocale { get; set; }
    public bool? KyiAiDebugHeadful { get; set; }
    public bool? AwesomeIndieDebugHeadful { get; set; }
    public bool? NewAIForYouDebugHeadful { get; set; }
    public string? FullDescription { get; set; }
    public string? IconPath { get; set; }
    public string? HomepageUrl { get; set; }
    public string? PricingUrl { get; set; }
    public string? Type { get; set; }
    public string? Monetization { get; set; }
    public string? Status { get; set; }
    public string? Platforms { get; set; }
    public string? Features { get; set; }
    public string? SocialLinks { get; set; }
    public string? YouTubeVideoUrl { get; set; }
    public string? AlternativeSocialLinkType { get; set; }
    public string? AlternativePricingName { get; set; }
    public string? AlternativePricingCost { get; set; }
    public string? Synonyms { get; set; }
    public string? PreLaunchUrl { get; set; }
    public string? LaunchpadUrl { get; set; }
    public string? LaunchpadId { get; set; }
    public string? Creators { get; set; }
    public string? ProductImages { get; set; }
    public string? EnablePreLaunchPreview { get; set; }
    public string? CreateFirstComment { get; set; }
}

public class SubmitJobProgressDto
{
    public Guid JobId { get; set; }
    public string WebsiteUrl { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
    public List<SubmitJobDetailProgressDto> Details { get; set; } = new();
}

public class SubmitJobDetailProgressDto
{
    public Guid DetailId { get; set; }
    public string PlatformName { get; set; } = string.Empty;
    public string PlatformCode { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public string? ErrorMessage { get; set; }
    public string? ResponseData { get; set; }
    public DateTime UpdatedAt { get; set; }
    public List<SubmitAuditLogDto> AuditLogs { get; set; } = new();
}

public class SubmitAuditLogDto
{
    public Guid Id { get; set; }
    public string Action { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public string? LogContent { get; set; }
    public int? DurationMs { get; set; }
    public DateTime Timestamp { get; set; }
}
