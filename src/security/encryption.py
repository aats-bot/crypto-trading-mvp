"""
Encryption utilities for API keys and sensitive data
"""
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from config.settings import settings

logger = logging.getLogger(__name__)


class EncryptionManager:
    """Manages encryption and decryption of sensitive data"""
    
    def __init__(self):
        self._fernet = None
        self._init_encryption()
    
    def _init_encryption(self):
        """Initialize encryption with key derivation"""
        try:
            # Use encryption key from settings or generate one
            password = settings.encryption_key.encode()
            
            # Use a fixed salt for consistency (in production, store this securely)
            salt = b'crypto_trading_mvp_salt_2025'
            
            # Derive key using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            
            # Create Fernet instance
            self._fernet = Fernet(key)
            
            logger.info("Encryption manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing encryption: {e}")
            raise
    
    def encrypt(self, data: str) -> str:
        """Encrypt a string"""
        try:
            if not data:
                return ""
            
            encrypted_data = self._fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
            
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt a string"""
        try:
            if not encrypted_data:
                return ""
            
            # Decode from base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            
            # Decrypt
            decrypted_data = self._fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode()
            
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise


# Global encryption manager instance
_encryption_manager = None


def get_encryption_manager() -> EncryptionManager:
    """Get global encryption manager instance"""
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
    return _encryption_manager


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key"""
    return get_encryption_manager().encrypt(api_key)


def decrypt_api_key(encrypted_api_key: str) -> str:
    """Decrypt an API key"""
    return get_encryption_manager().decrypt(encrypted_api_key)


def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data"""
    return get_encryption_manager().encrypt(data)


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    return get_encryption_manager().decrypt(encrypted_data)


def generate_encryption_key() -> str:
    """Generate a new encryption key"""
    return Fernet.generate_key().decode()


def test_encryption():
    """Test encryption/decryption functionality"""
    try:
        test_data = "test_api_key_12345"
        
        # Encrypt
        encrypted = encrypt_api_key(test_data)
        logger.info(f"Encrypted: {encrypted}")
        
        # Decrypt
        decrypted = decrypt_api_key(encrypted)
        logger.info(f"Decrypted: {decrypted}")
        
        # Verify
        if test_data == decrypted:
            logger.info("✅ Encryption test passed!")
            return True
        else:
            logger.error("❌ Encryption test failed!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Encryption test error: {e}")
        return False


if __name__ == "__main__":
    # Test encryption when run directly
    logging.basicConfig(level=logging.INFO)
    test_encryption()

