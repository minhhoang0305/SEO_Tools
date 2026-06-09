namespace SeoAudit.Application.Interfaces;

public interface ICryptographyService
{
    (string CipherText, string Iv) Encrypt(string plainText);
    string Decrypt(string cipherText, string iv);
}
