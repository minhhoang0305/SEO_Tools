using IdentityService.Domain.Models;
namespace IdentityService.Domain.Interfaces;

public interface IRegisterRepository
{
    Task AddAsync(Register register);
    Task<Register?> GetByTokenAsync(string token);
    Task<Register?> GetByIdAsync(Guid id);
    Task UpdateAsync(Register register);
    Task DeleteAsync(Guid id);
}