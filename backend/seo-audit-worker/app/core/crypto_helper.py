import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from app.core.config import ENCRYPTION_KEY

def decrypt_credential(encrypted_data_b64: str, iv_b64: str) -> str:
    """
    Giải mã thông tin nhạy cảm (như passwords/cookies) được mã hóa bằng AES-256-CBC từ phía C#.
    """
    if not encrypted_data_b64 or not iv_b64:
        return ""
    
    try:
        # 1. Băm khóa cấu hình bằng SHA256 để lấy đúng 32 bytes (256-bit)
        key_bytes = hashlib.sha256(ENCRYPTION_KEY.encode('utf-8')).digest()
        
        # 2. Giải mã dữ liệu Base64
        cipher_bytes = base64.b64decode(encrypted_data_b64)
        iv_bytes = base64.b64decode(iv_b64)
        
        # 3. Giải mã AES CBC
        cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv_bytes), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(cipher_bytes) + decryptor.finalize()
        
        # 4. Loại bỏ PKCS7 padding
        unpadder = padding.PKCS7(128).unpadder()
        decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
        
        return decrypted.decode('utf-8')
    except Exception as e:
        print(f"Lỗi giải mã Credential: {e}")
        return ""
