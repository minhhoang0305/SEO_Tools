using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using Microsoft.Extensions.Configuration;
using SeoAudit.Application.Interfaces;

namespace SeoAudit.Infrastructure.Services;

public class CryptographyService : ICryptographyService
{
    private readonly byte[] _key;

    public CryptographyService(IConfiguration configuration)
    {
        var keyString = configuration["Encryption:Key"] ?? "seo_tools_default_super_secret_key_32bytes!!";
        
        // Dùng SHA256 băm cấu hình key để luôn đảm bảo độ dài khóa chính xác là 32 bytes (256-bit) cho AES-256
        using var sha256 = SHA256.Create();
        _key = sha256.ComputeHash(Encoding.UTF8.GetBytes(keyString));
    }

    public (string CipherText, string Iv) Encrypt(string plainText)
    {
        if (string.IsNullOrEmpty(plainText))
            return (string.Empty, string.Empty);

        using var aes = Aes.Create();
        aes.Key = _key;
        aes.GenerateIV();

        using var encryptor = aes.CreateEncryptor(aes.Key, aes.IV);
        using var ms = new MemoryStream();
        using (var cs = new CryptoStream(ms, encryptor, CryptoStreamMode.Write))
        using (var sw = new StreamWriter(cs))
        {
            sw.Write(plainText);
        }

        return (Convert.ToBase64String(ms.ToArray()), Convert.ToBase64String(aes.IV));
    }

    public string Decrypt(string cipherText, string iv)
    {
        if (string.IsNullOrEmpty(cipherText) || string.IsNullOrEmpty(iv))
            return string.Empty;

        var ivBytes = Convert.FromBase64String(iv);
        var buffer = Convert.FromBase64String(cipherText);

        using var aes = Aes.Create();
        aes.Key = _key;
        aes.IV = ivBytes;

        using var decryptor = aes.CreateDecryptor(aes.Key, aes.IV);
        using var ms = new MemoryStream(buffer);
        using var cs = new CryptoStream(ms, decryptor, CryptoStreamMode.Read);
        using var sr = new StreamReader(cs);

        return sr.ReadToEnd();
    }
}
