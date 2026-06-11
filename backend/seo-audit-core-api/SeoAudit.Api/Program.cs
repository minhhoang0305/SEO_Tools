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
