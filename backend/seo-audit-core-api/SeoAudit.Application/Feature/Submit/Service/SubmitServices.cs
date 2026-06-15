using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using SeoAudit.Application.Feature.Submit.Contract;
using SeoAudit.Application.Interfaces;
using SeoAudit.Domain.Entities;
using SeoAudit.Domain.Enum;
using SeoAudit.Domain.Interfaces;
using SeoAudit.Shared;

namespace SeoAudit.Application.Features;

public class SaveCredentialService(
    ISubmitRepository submitRepository,
    ICryptographyService cryptographyService)
{
    public async Task Handle(
        SaveCredentialRequest request,
        Guid userId,
        CancellationToken cancellationToken)
    {
        // 1. Mã hóa dữ liệu nhạy cảm bằng AES-256
        var (cipherText, iv) = cryptographyService.Encrypt(request.CredentialData);

        // 2. Tạo đối tượng Credential
        var credential = new PlatformCredential
        {
            Id = Guid.NewGuid(),
            PlatformId = request.PlatformId,
            UserId = userId,
            EncryptedData = cipherText,
            IV = iv,
            UpdatedAt = DateTime.UtcNow
        };

        // 3. Lưu vào database
        await submitRepository.SaveCredentialAsync(credential, cancellationToken);
    }
}

public class RequestPlatformConnectService(
    ISubmitRepository submitRepository,
    IMessagePublisher publisher)
{
    public async Task<Guid> Handle(
        ConnectPlatformRequest request,
        Guid userId,
        CancellationToken cancellationToken)
    {
        var platform = await submitRepository.GetPlatformByIdAsync(request.PlatformId, cancellationToken);
        if (platform == null)
        {
            throw new InvalidOperationException("Platform không tồn tại.");
        }

        var requestId = Guid.NewGuid();
        await publisher.PublishAsync(
            "platform.connect.requested",
            new PlatformConnectRequestedEvent
            {
                RequestId = requestId,
                UserId = userId,
                PlatformId = platform.Id,
                PlatformCode = platform.Code,
                PlatformName = platform.Name
            },
            cancellationToken);

        return requestId;
    }
}

public class CreateSubmitJobService(
    ISubmitRepository submitRepository,
    IMessagePublisher publisher)
{
    public async Task<Guid> Handle(
        CreateSubmitJobRequest request,
        Guid userId,
        CancellationToken cancellationToken)
    {
        // 1. Tổ chức dữ liệu metadata tùy chọn làm JSON
        var metadata = new Dictionary<string, string>();
        if (!string.IsNullOrWhiteSpace(request.SiteName)) metadata["SiteName"] = request.SiteName;
        if (!string.IsNullOrWhiteSpace(request.Tagline)) metadata["Tagline"] = request.Tagline;
        if (!string.IsNullOrWhiteSpace(request.Description)) metadata["Description"] = request.Description;
        if (!string.IsNullOrWhiteSpace(request.ProductDescription)) metadata["ProductDescription"] = request.ProductDescription;
        if (!string.IsNullOrWhiteSpace(request.Keywords)) metadata["Keywords"] = request.Keywords;
        if (!string.IsNullOrWhiteSpace(request.Categories)) metadata["Categories"] = request.Categories;
        if (!string.IsNullOrWhiteSpace(request.Category)) metadata["Category"] = request.Category;
        if (!string.IsNullOrWhiteSpace(request.Stacks)) metadata["Stacks"] = request.Stacks;
        if (!string.IsNullOrWhiteSpace(request.ProductType)) metadata["ProductType"] = request.ProductType;
        if (!string.IsNullOrWhiteSpace(request.LaunchPlan)) metadata["LaunchPlan"] = request.LaunchPlan;
        if (!string.IsNullOrWhiteSpace(request.LaunchWeek)) metadata["LaunchWeek"] = request.LaunchWeek;
        // if (!string.IsNullOrWhiteSpace(request.SitemapUrl)) metadata["SitemapUrl"] = request.SitemapUrl;
        // if (!string.IsNullOrWhiteSpace(request.ContactEmail)) metadata["ContactEmail"] = request.ContactEmail;
        if (!string.IsNullOrWhiteSpace(request.YourName)) metadata["YourName"] = request.YourName;
        if (!string.IsNullOrWhiteSpace(request.Pricing)) metadata["Pricing"] = request.Pricing;
        if (!string.IsNullOrWhiteSpace(request.NewsletterOptIn)) metadata["NewsletterOptIn"] = request.NewsletterOptIn;
        if (!string.IsNullOrWhiteSpace(request.PreLaunchUrl)) metadata["PreLaunchUrl"] = request.PreLaunchUrl;
        if (!string.IsNullOrWhiteSpace(request.LaunchpadUrl)) metadata["LaunchpadUrl"] = request.LaunchpadUrl;
        if (!string.IsNullOrWhiteSpace(request.LaunchpadId)) metadata["LaunchpadId"] = request.LaunchpadId;
        if (!string.IsNullOrWhiteSpace(request.Creators)) metadata["Creators"] = request.Creators;
        if (!string.IsNullOrWhiteSpace(request.ProductImages)) metadata["ProductImages"] = request.ProductImages;
        if (!string.IsNullOrWhiteSpace(request.EnablePreLaunchPreview)) metadata["EnablePreLaunchPreview"] = request.EnablePreLaunchPreview;
        if (!string.IsNullOrWhiteSpace(request.CreateFirstComment)) metadata["CreateFirstComment"] = request.CreateFirstComment;
        
        var payloadJson = JsonSerializer.Serialize(metadata);

        // 2. Tạo thực thể SubmitJob chính
        var job = new SubmitJob
        {
            Id = Guid.NewGuid(),
            UserId = userId,
            WebsiteUrl = request.WebsiteUrl,
            Payload = payloadJson,
            Status = SubmitStatus.Pending,
            CreatedAt = DateTime.UtcNow
        };

        var platforms = await submitRepository.GetActivePlatformsAsync(cancellationToken);
        var activePlatformDict = platforms.ToDictionary(p => p.Id);

        var eventPlatforms = new List<PlatformSubmitInfo>();

        // 3. Tạo SubmitJobDetail cho từng platform được chọn
        foreach (var platformId in request.PlatformIds)
        {
            if (!activePlatformDict.TryGetValue(platformId, out var platform))
            {
                continue; // Bỏ qua nếu platform không tồn tại hoặc không active
            }

            var detail = new SubmitJobDetail
            {
                Id = Guid.NewGuid(),
                JobId = job.Id,
                PlatformId = platformId,
                Status = SubmitStatus.Pending,
                UpdatedAt = DateTime.UtcNow
            };
            job.Details.Add(detail);

            // Tìm credential đã cấu hình của user đối với platform này
            var credential = await submitRepository.GetCredentialAsync(userId, platformId, cancellationToken);

            eventPlatforms.Add(new PlatformSubmitInfo
            {
                JobDetailId = detail.Id,
                PlatformId = platformId,
                PlatformCode = platform.Code,
                SubmitMethod = platform.SubmitMethod,
                EncryptedCredential = credential?.EncryptedData,
                IV = credential?.IV
            });
        }

        if (job.Details.Count == 0)
        {
            throw new InvalidOperationException("Phải chọn ít nhất một Platform hợp lệ để submit.");
        }

        // 4. Ghi nhận vào Database
        await submitRepository.AddJobAsync(job, cancellationToken);

        // 5. Đẩy tin nhắn vào RabbitMQ để Worker xử lý bất đồng bộ
        var submitCreatedEvent = new SubmitJobCreatedEvent
        {
            JobId = job.Id,
            WebsiteUrl = job.WebsiteUrl,
            Payload = payloadJson,
            Platforms = eventPlatforms
        };

        await publisher.PublishAsync(
            "submit.created",
            submitCreatedEvent,
            cancellationToken);

        return job.Id;
    }
}
