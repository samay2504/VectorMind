"""
Encryption utilities for field-level data protection
Provides AES encryption for sensitive data at rest
"""

import logging
import base64
from typing import Any, Optional, Dict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class EncryptionHelper:
    """Helper for encrypting and decrypting sensitive data"""
    
    def __init__(self, encryption_key: Optional[str] = None, salt: Optional[bytes] = None):
        """
        Initialize encryption helper
        
        Args:
            encryption_key: Base encryption key (if None, generates new key)
            salt: Salt for key derivation (if None, uses default)
        """
        self.salt = salt or b'multimodal_rag_salt_2024'  # Should be random in production
        
        if encryption_key:
            self._key = self._derive_key(encryption_key)
        else:
            # Generate new key
            self._key = Fernet.generate_key()
        
        self._fernet = Fernet(self._key)
        logger.info("Encryption helper initialized")
    
    def _derive_key(self, password: str) -> bytes:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: Base password/key
        
        Returns:
            Derived key bytes
        """
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string
        
        Args:
            plaintext: String to encrypt
        
        Returns:
            Encrypted string (base64 encoded)
        """
        try:
            if not plaintext:
                return ""
            
            encrypted_bytes = self._fernet.encrypt(plaintext.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
        
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext string
        
        Args:
            ciphertext: Encrypted string (base64 encoded)
        
        Returns:
            Decrypted plaintext
        """
        try:
            if not ciphertext:
                return ""
            
            encrypted_bytes = base64.urlsafe_b64decode(ciphertext.encode('utf-8'))
            decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def encrypt_dict(self, data: Dict[str, Any], fields_to_encrypt: list) -> Dict[str, Any]:
        """
        Encrypt specific fields in a dictionary
        
        Args:
            data: Dictionary with data
            fields_to_encrypt: List of field names to encrypt
        
        Returns:
            Dictionary with encrypted fields
        """
        encrypted_data = data.copy()
        
        for field in fields_to_encrypt:
            if field in encrypted_data and encrypted_data[field]:
                try:
                    value = str(encrypted_data[field])
                    encrypted_data[field] = self.encrypt(value)
                    encrypted_data[f"{field}_encrypted"] = True
                except Exception as e:
                    logger.error(f"Failed to encrypt field {field}: {e}")
        
        return encrypted_data
    
    def decrypt_dict(self, data: Dict[str, Any], fields_to_decrypt: list) -> Dict[str, Any]:
        """
        Decrypt specific fields in a dictionary
        
        Args:
            data: Dictionary with encrypted data
            fields_to_decrypt: List of field names to decrypt
        
        Returns:
            Dictionary with decrypted fields
        """
        decrypted_data = data.copy()
        
        for field in fields_to_decrypt:
            if field in decrypted_data and decrypted_data.get(f"{field}_encrypted"):
                try:
                    decrypted_data[field] = self.decrypt(decrypted_data[field])
                    decrypted_data[f"{field}_encrypted"] = False
                except Exception as e:
                    logger.error(f"Failed to decrypt field {field}: {e}")
        
        return decrypted_data
    
    def hash_value(self, value: str) -> str:
        """
        Create a one-way hash of a value (for comparison without decryption)
        
        Args:
            value: Value to hash
        
        Returns:
            Hashed value (hex)
        """
        import hashlib
        return hashlib.sha256(value.encode('utf-8')).hexdigest()
    
    def get_key_fingerprint(self) -> str:
        """
        Get a fingerprint of the encryption key (for verification)
        
        Returns:
            Key fingerprint
        """
        import hashlib
        return hashlib.sha256(self._key).hexdigest()[:16]
    
    @staticmethod
    def generate_key() -> str:
        """
        Generate a new encryption key
        
        Returns:
            Base64-encoded key
        """
        key = Fernet.generate_key()
        return key.decode('utf-8')


class SecureStorage:
    """Secure storage wrapper for sensitive data"""
    
    def __init__(self, encryption_helper: EncryptionHelper):
        """
        Initialize secure storage
        
        Args:
            encryption_helper: Encryption helper instance
        """
        self.encryptor = encryption_helper
        self._cache = {}
    
    def store(self, key: str, value: str, encrypt: bool = True) -> None:
        """
        Store a value securely
        
        Args:
            key: Storage key
            value: Value to store
            encrypt: Whether to encrypt the value
        """
        if encrypt:
            stored_value = self.encryptor.encrypt(value)
        else:
            stored_value = value
        
        self._cache[key] = {
            "value": stored_value,
            "encrypted": encrypt
        }
    
    def retrieve(self, key: str) -> Optional[str]:
        """
        Retrieve a value securely
        
        Args:
            key: Storage key
        
        Returns:
            Retrieved value (decrypted if necessary)
        """
        if key not in self._cache:
            return None
        
        item = self._cache[key]
        
        if item["encrypted"]:
            return self.encryptor.decrypt(item["value"])
        else:
            return item["value"]
    
    def delete(self, key: str) -> bool:
        """
        Delete a stored value
        
        Args:
            key: Storage key
        
        Returns:
            True if deleted
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def list_keys(self) -> list:
        """Get all stored keys"""
        return list(self._cache.keys())


class TokenEncryptor:
    """Specialized encryptor for API tokens and secrets"""
    
    def __init__(self, master_key: str):
        """
        Initialize token encryptor
        
        Args:
            master_key: Master encryption key
        """
        self.helper = EncryptionHelper(master_key)
    
    def encrypt_token(self, token: str, token_type: str = "api") -> Dict[str, str]:
        """
        Encrypt an API token or secret
        
        Args:
            token: Token to encrypt
            token_type: Type of token
        
        Returns:
            Dictionary with encrypted token and metadata
        """
        encrypted = self.helper.encrypt(token)
        token_hash = self.helper.hash_value(token)
        
        return {
            "encrypted_token": encrypted,
            "token_hash": token_hash,
            "token_type": token_type,
            "key_fingerprint": self.helper.get_key_fingerprint()
        }
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """
        Decrypt an API token
        
        Args:
            encrypted_token: Encrypted token
        
        Returns:
            Decrypted token
        """
        return self.helper.decrypt(encrypted_token)
    
    def verify_token(self, token: str, token_hash: str) -> bool:
        """
        Verify a token matches its hash without decryption
        
        Args:
            token: Token to verify
            token_hash: Expected hash
        
        Returns:
            True if token matches
        """
        computed_hash = self.helper.hash_value(token)
        return computed_hash == token_hash
