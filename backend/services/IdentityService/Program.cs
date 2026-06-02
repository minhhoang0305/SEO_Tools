using IdentityService.Application.Services;
using IdentityService.Domain.Interfaces;
using IdentityService.Infrastructure.Persistence.Data;
using IdentityService.Infrastructure.Repository;
using IdentityService.Infrastructure.Email;
using Microsoft.EntityFrameworkCore;
using IdentityService.Api.Middleware;
using IdentityService.Infrastructure.Options;



var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();



builder.Services.AddOpenApi();
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));

builder.Services.AddScoped<IUserService, UserRepository>();
builder.Services.AddScoped<IRegisterRepository, RegisterRepository>();
builder.Services.AddScoped<RegisterService>();
builder.Services.Configure<SmtpOptions>(builder.Configuration.GetSection(SmtpOptions.SectionName));
builder.Services.AddScoped<IEmailSender, SmtpEmailSender>();
builder.Services.AddScoped<IAuthRepository, AuthRepository>();
builder.Services.AddScoped<LoginService>();
builder.Services.AddScoped<IRefreshService, RefreshService>();
builder.Services.AddScoped<IJwtService, JwtService>();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

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


app.UseMiddleware<TraceIdMiddleware>();
app.UseHttpsRedirection();
app.UseMiddleware<RequestLoggingMiddleware>();
app.MapControllers();
app.Run();