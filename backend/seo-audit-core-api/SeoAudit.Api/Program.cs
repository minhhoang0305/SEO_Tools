using FirebaseAdmin;
using Google.Apis.Auth.OAuth2;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using SeoAudit.Application.Feature.Auth;
using SeoAudit.Domain.Interfaces;
using SeoAudit.Infrastructure.Persistence.Data;
using SeoAudit.Infrastructure.Repository;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();

builder.Services.AddDbContext<AppDbContext>(options =>
{
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection"));
});

builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<IAuthService, AuthService>();

var firebaseProjectId = builder.Configuration["Firebase:ProjectId"];

if (string.IsNullOrWhiteSpace(firebaseProjectId))
{
    throw new InvalidOperationException("Firebase:ProjectId is required.");
}

if (FirebaseApp.DefaultInstance is null)
{
    FirebaseApp.Create(new AppOptions
    {
        ProjectId = firebaseProjectId,
        Credential = GoogleCredential.GetApplicationDefault()
    });
}

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

var app = builder.Build();


if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

app.UseAuthentication();
app.UseAuthorization();

app.MapGet("/health", () => Results.Ok(new { status = "ok" }));

app.MapControllers();

app.Run();