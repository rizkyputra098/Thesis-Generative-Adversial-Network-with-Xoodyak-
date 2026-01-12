"""
xoodyak_utils.py - FIXED VERSION
Helper functions untuk Xoodyak encryption/decryption dengan perbaikan
"""

import hashlib
import os
from typing import Tuple
from xoodyak_core import XoodyakAEAD


def derive_key(password: str) -> bytes:
    """
    Derive 128-bit key dari password dengan normalisasi
    
    Args:
        password: User password (string)
        
    Returns:
        128-bit key (16 bytes)
    """
    # FIX 1: Normalisasi password - hapus whitespace dan lowercase
    password = password.strip()
    
    # FIX 2: Gunakan UTF-8 encoding yang konsisten
    password_bytes = password.encode('utf-8')
    
    # FIX 3: Salt yang konsisten
    salt = b'xoodyak_salt_key'
    
    # Derive key
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password_bytes,
        salt,
        100000
    )[:16]
    
    return key


def calculate_hash(data: bytes) -> str:
    """
    Calculate MD5 hash untuk integrity verification
    """
    return hashlib.md5(data).hexdigest()


def encrypt_file(file_data: bytes, password: str, filename: str = '') -> bytes:
    """
    Encrypt file using Xoodyak AEAD dengan format yang konsisten
    
    Format: VERSION (1) + NONCE (16) + TAG (16) + CIPHERTEXT
    Associated Data: kosong (b'')
    
    Args:
        file_data: Raw file data (bytes)
        password: Encryption password
        filename: Original filename (metadata only)
        
    Returns:
        Encrypted package (bytes)
    """
    # FIX 4: Normalisasi password
    password = password.strip()
    
    # Derive key dari password
    key = derive_key(password)
    
    # Generate random nonce (128-bit = 16 bytes)
    nonce = os.urandom(16)
    
    # FIX 5: Associated data HARUS kosong - JANGAN UBAH
    ad = b''
    
    try:
        # Encrypt using Xoodyak AEAD
        aead = XoodyakAEAD(key, nonce, ad)
        ciphertext, tag = aead.encrypt(file_data)
        
        # FIX 6: Package format dengan version byte
        # VERSION (1 byte) + NONCE (16 bytes) + TAG (16 bytes) + CIPHERTEXT
        version = b'\x01'
        encrypted_package = version + nonce + tag + ciphertext
        
        return encrypted_package
    
    except Exception as e:
        raise ValueError(f"Enkripsi gagal: {str(e)}")


def decrypt_file(package_data: bytes, password: str) -> Tuple[bytes, dict, bool]:
    """
    Decrypt file using Xoodyak AEAD dengan validasi ketat
    
    Format: VERSION (1) + NONCE (16) + TAG (16) + CIPHERTEXT
    
    Args:
        package_data: Encrypted package (bytes)
        password: Decryption password
        
    Returns:
        (plaintext, info_dict, is_verified): Tuple containing:
            - plaintext: Decrypted data
            - info_dict: File information
            - is_verified: Authentication status
            
    Raises:
        ValueError: If decryption fails
    """
    try:
        # FIX 7: Normalisasi password
        password = password.strip()
        
        # Derive key dari password
        key = derive_key(password)
        
        # FIX 8: Validasi minimum size
        # Minimum: VERSION (1) + NONCE (16) + TAG (16) = 33 bytes
        if len(package_data) < 33:
            raise ValueError("Data terlalu kecil atau format rusak")
        
        # FIX 9: Parse package dengan benar
        # VERSION (1 byte) + NONCE (16 bytes) + TAG (16 bytes) + CIPHERTEXT
        version = package_data[0:1]
        nonce = package_data[1:17]
        tag = package_data[17:33]
        ciphertext = package_data[33:]
        
        # FIX 10: Validasi version
        if version != b'\x01':
            raise ValueError("Format file tidak valid atau versi tidak kompatibel")
        
        # FIX 11: Validasi nonce length
        if len(nonce) != 16:
            raise ValueError("Nonce invalid - data mungkin rusak")
        
        # FIX 12: Validasi tag length
        if len(tag) != 16:
            raise ValueError("Tag invalid - data mungkin rusak")
        
        # FIX 13: Associated data HARUS kosong - IDENTIK dengan enkripsi
        ad = b''
        
        # Decrypt using Xoodyak AEAD
        aead = XoodyakAEAD(key, nonce, ad)
        plaintext, is_verified = aead.decrypt(ciphertext, tag)
        
        # FIX 14: Detailed authentication check
        if not is_verified:
            raise ValueError(
                "❌ AUTENTIKASI GAGAL!\n"
                "Kemungkinan penyebab:\n"
                "1. Password salah\n"
                "2. Data gambar rusak atau termodifikasi\n"
                "3. File enkripsi tidak lengkap"
            )
        
        # Prepare result info
        result = {
            'file_size': len(plaintext),
            'is_authenticated': is_verified,
            'algorithm': 'Xoodyak AEAD (NIST Standard)',
            'nonce_hex': nonce.hex(),
            'tag_hex': tag.hex()
        }
        
        return plaintext, result, is_verified
    
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise ValueError(f"Dekripsi gagal: {str(e)}")


def is_file_encrypted(data: bytes) -> bool:
    """
    Check if file is encrypted dengan validasi format
    
    Encrypted file minimal: VERSION (1) + NONCE (16) + TAG (16) = 33 bytes
    """
    if len(data) < 33:
        return False
    
    # Check version byte
    if data[0:1] != b'\x01':
        return False
    
    # Check known plaintext signatures
    known_signatures = [
        b'PK',           # ZIP, DOCX, XLSX
        b'%PDF',         # PDF
        b'\xff\xd8\xff', # JPEG
        b'\x89PNG',      # PNG
        b'GIF8',         # GIF
        b'BM',           # BMP
        b'\x1f\x8b',     # GZIP
    ]
    
    for sig in known_signatures:
        if data.startswith(sig):
            return False
    
    return True


def get_file_info(data: bytes, filename: str = '') -> dict:
    """
    Get file information dengan status enkripsi
    """
    return {
        'filename': filename,
        'size': len(data),
        'hash': calculate_hash(data),
        'is_encrypted': is_file_encrypted(data)
    }


def verify_encryption_consistency(password: str, iterations: int = 3) -> dict:
    """
    FIX 15: Verify bahwa derive_key konsisten untuk password yang sama
    
    Gunakan fungsi ini untuk debugging
    """
    results = []
    for i in range(iterations):
        key = derive_key(password)
        results.append(key.hex())
    
    return {
        'password': password,
        'keys_generated': results,
        'all_identical': len(set(results)) == 1,
        'status': '✅ KONSISTEN' if len(set(results)) == 1 else '❌ TIDAK KONSISTEN'
    }