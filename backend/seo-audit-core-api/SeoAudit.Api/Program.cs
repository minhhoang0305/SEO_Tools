using FirebaseAdmin;
using FirebaseAdmin.Auth;
using Google.Apis.Auth.OAuth2;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using RabbitMQ.Client;
using SeoAudit.Application.Feature.Auth;
using SeoAudit.Application.Feature.Auth.Interfaces;
using SeoAudit.Application.Feature.Auth.Service;
using SeoAudit.Application.Features;
using SeoAudit.Application.Interfaces;
using SeoAudit.Application.Options;
using SeoAudit.Domain.Interfaces;
using SeoAudit.Domain.Entities;
using SeoAudit.Infrastructure.Messaging;
using SeoAudit.Infrastructure.Persistence.Data;
using SeoAudit.Infrastructure.Repositories;
using SeoAudit.Infrastructure.Repository;
using SeoAudit.Infrastructure.Services;
using StackExchange.Redis;
using System.Threading.RateLimiting;
using System.Diagnostics;
using SeoAudit.Api;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        options.JsonSerializerOptions.Converters.Add(new System.Text.Json.Serialization.JsonStringEnumConverter());
    });

builder.Services.AddDbContext<AppDbContext>(options =>
{
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection"));
});

builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<IAuthService, AuthService>();
builder.Services.AddScoped<IJwtService, JwtService>();
builder.Services.AddScoped<IRefreshService, RefreshService>();
builder.Services.AddScoped<CreateAuditService>();
builder.Services.AddScoped<IAuditRepository, AuditRepository>();
builder.Services.AddScoped<IMessagePublisher, RabbitMqPublisher>();
builder.Services.AddScoped<ISubmitRepository, SubmitRepository>();
builder.Services.AddScoped<ICryptographyService, CryptographyService>();
builder.Services.AddScoped<SaveCredentialService>();
builder.Services.AddScoped<CreateSubmitJobService>();

builder.Services.Configure<JwtOptions>(builder.Configuration.GetSection(JwtOptions.SectionName));

var redisConnectionString = builder.Configuration["Redis:ConnectionString"] ?? "localhost:6379";
builder.Services.AddSingleton<IConnectionMultiplexer>(sp =>
{
    return ConnectionMultiplexer.Connect(redisConnectionString);
});

builder.Services.AddSingleton<IConnectionFactory>(_ => new ConnectionFactory
{
    HostName = builder.Configuration["RabbitMq:HostName"] ?? "localhost",
    Port = builder.Configuration.GetValue("RabbitMq:Port", 5672),
    UserName = builder.Configuration["RabbitMq:UserName"] ?? "guest",
    Password = builder.Configuration["RabbitMq:Password"] ?? "guest"
});

var firebaseProjectId = builder.Configuration["Firebase:ProjectId"];

if (string.IsNullOrWhiteSpace(firebaseProjectId))
{
    throw new InvalidOperationException("Firebase:ProjectId is required.");
}

var firebaseApp = FirebaseApp.DefaultInstance;

if (firebaseApp is null)
{
    firebaseApp = FirebaseApp.Create(new AppOptions
    {
        ProjectId = firebaseProjectId,
        Credential = GoogleCredential.GetApplicationDefault()
    });
}

builder.Services.AddSingleton(FirebaseAuth.GetAuth(firebaseApp));

builder.Services
    .AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.Authority = $"https://securetoken.google.com/{firebaseProjectId}";
        options.TokenValidationParameters.ValidIssuer = $"https://securetoken.google.com/{firebaseProjectId}";
        options.TokenValidationParameters.ValidAudience = firebaseProjectId;
    });

builder.Services.AddAuthorization();
builder.Services.AddSwaggerGen();

builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

builder.Services.AddRateLimiter(options =>
{
    options.GlobalLimiter = PartitionedRateLimiter.Create<HttpContext, string>(httpContext =>
        RateLimitPartition.GetFixedWindowLimiter(
            partitionKey: httpContext.User.Identity?.Name ?? httpContext.Request.Headers.Host.ToString(), 
            factory: partition => new FixedWindowRateLimiterOptions
            {
                AutoReplenishment = true,
                PermitLimit = 100,
                QueueLimit = 0,
                Window = TimeSpan.FromMinutes(1)
            }));
    
    options.OnRejected = (context, cancellationToken) =>
    {
        if (context.Lease.TryGetMetadata(MetadataName.RetryAfter, out var retryAfter))
        {
            context.HttpContext.Response.Headers.RetryAfter = retryAfter.TotalSeconds.ToString();
        }

        context.HttpContext.Response.StatusCode = StatusCodes.Status429TooManyRequests;
        context.HttpContext.Response.WriteAsync("Too many requests. Please try again later.");

        return new ValueTask();
    };
});

Activity.DefaultIdFormat = ActivityIdFormat.W3C;
Activity.ForceDefaultIdFormat = true;

var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    app.ConfigureExceptionHandler();
}

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    await db.Database.MigrateAsync();

    var seedPlatforms = new[]
    {
        new SeoPlatform
        {
            Id = Guid.Parse("d0a1b2c3-4d5e-4f60-8a71-9b0c1d2e3f40"),
            Name = "10words",
            Code = "10words",
            WebsiteUrl = "https://portal.10words.io/submissions",
            SubmitMethod = "UI_Automation",
            IsActive = true,
            CreatedAt = DateTime.UtcNow
        },
        new SeoPlatform
        {
            Id = Guid.Parse("b5a7c0d1-4e5f-4d25-9a2f-8b4b1c6d7e8f"),
            Name = "BAI.tools",
            Code = "baitools",
            WebsiteUrl = "https://bai.tools/submit-ai-tools",
            SubmitMethod = "UI_Automation",
            IsActive = true,
            CreatedAt = DateTime.UtcNow
        },
        new SeoPlatform
        {
            Id = Guid.Parse("c7f7d0b8-5d3c-4a56-9c69-9f2bf2e6d911"),
            Name = "ProductBurst",
            Code = "productburst",
            WebsiteUrl = "https://productburst.com",
            SubmitMethod = "UI_Automation",
            IsActive = true,
            CreatedAt = DateTime.UtcNow
        },
        new SeoPlatform
        {
            Id = Guid.Parse("c2f9c6d0-8e5c-4e0b-a5d8-5a7d4f0ef2b1"),
            Name = "Kyi AI",
            Code = "kyi_ai",
            WebsiteUrl = "https://kyi.ai",
            SubmitMethod = "UI_Automation",
            IsActive = true,
            CreatedAt = DateTime.UtcNow
        },
        new SeoPlatform
        {
            Id = Guid.Parse("e7d3b6a2-2a77-4f7d-9e61-8cf1db3d1c23"),
            Name = "Awesome Indie",
            Code = "awesome_indie",
            WebsiteUrl = "https://awesomeindie.com",
            SubmitMethod = "UI_Automation",
            IsActive = true,
            CreatedAt = DateTime.UtcNow
        },
        new SeoPlatform
        {
            Id = Guid.Parse("7b1a2c3d-4e5f-4a6b-8c9d-1e2f3a4b5c6d"),
            Name = "New AI For You",
            Code = "newaiforyou",
            WebsiteUrl = "https://newaiforyou.com",
            SubmitMethod = "UI_Automation",
            IsActive = true,
            CreatedAt = DateTime.UtcNow
        },
        new SeoPlatform
        {
            Id = Guid.Parse("d4f0d2a4-0f33-4a71-9f54-8e6c5a3b4a55"),
            Name = "Future Tools",
            Code = "futuretools",
            WebsiteUrl = "https://futuretools.io/submit-a-tool",
            SubmitMethod = "UI_Automation",
            IsActive = true,
            CreatedAt = DateTime.UtcNow
        },
        new SeoPlatform
        {
            Id = Guid.Parse("a3b4c5d6-7e8f-4012-9abc-3d4e5f607182"),
            Name = "Alternative",
            Code = "alternative",
            WebsiteUrl = "https://alternative.me/software-submission",
            SubmitMethod = "UI_Automation",
            IsActive = true,
            CreatedAt = DateTime.UtcNow
        }
    };

    foreach (var seedPlatform in seedPlatforms)
    {
        var exists = await db.SeoPlatforms.AnyAsync(p => p.Code == seedPlatform.Code);
        if (!exists)
        {
            db.SeoPlatforms.Add(seedPlatform);
        }
    }

    await db.SaveChangesAsync();
}

app.UseHttpsRedirection();

app.UseCors();

app.UseMiddleware<TraceIdMiddleware>();
app.UseRateLimiter();
app.UseAuthentication();
app.UseAuthorization();
app.UseMiddleware<RequestLoggingMiddleware>();

app.MapGet("/health", () => Results.Ok(new { status = "ok" }));

app.MapControllers();

app.Run();
