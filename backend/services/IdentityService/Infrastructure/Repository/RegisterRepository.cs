using IdentityService.Domain.Interfaces;
using IdentityService.Domain.Models;
using IdentityService.Infrastructure.Persistence.Data;
using Microsoft.EntityFrameworkCore;

namespace IdentityService.Infrastructure.Repository;

public sealed class RegisterRepository : IRegisterRepository
{
    private readonly AppDbContext _dbContext;

    public RegisterRepository(AppDbContext dbContext)
    {
        _dbContext = dbContext;
    }

    public async Task AddAsync(Register register)
    {
        _dbContext.Registers.Add(register);
        await _dbContext.SaveChangesAsync();
    }

    public Task<Register?> GetByTokenAsync(string token)
    {
        return _dbContext.Registers.FirstOrDefaultAsync(register => register.VerificationToken == token);
    }

    public Task<Register?> GetByIdAsync(Guid id)
    {
        return _dbContext.Registers.FirstOrDefaultAsync(register => register.Id == id);
    }

    public async Task UpdateAsync(Register register)
    {
        _dbContext.Registers.Update(register);
        await _dbContext.SaveChangesAsync();
    }

    public async Task DeleteAsync(Guid id)
    {
        var register = await _dbContext.Registers.FirstOrDefaultAsync(register => register.Id == id);

        if (register is null)
        {
            return;
        }

        _dbContext.Registers.Remove(register);
        await _dbContext.SaveChangesAsync();
    }
}
