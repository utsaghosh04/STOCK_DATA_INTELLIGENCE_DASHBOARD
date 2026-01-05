"""
Simple in-memory cache for API responses
Can be replaced with Redis for production
"""
from datetime import datetime, timedelta
from typing import Optional, Any
import hashlib
import json

class SimpleCache:
    """Simple in-memory cache with TTL"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache = {}
        self.default_ttl = default_ttl
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = {
            'prefix': prefix,
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, prefix: str, *args, **kwargs) -> Optional[Any]:
        """Get value from cache"""
        key = self._generate_key(prefix, *args, **kwargs)
        
        if key in self.cache:
            value, expiry = self.cache[key]
            if datetime.now() < expiry:
                return value
            else:
                # Expired, remove it
                del self.cache[key]
        
        return None
    
    def set(self, prefix: str, value: Any, ttl: Optional[int] = None, *args, **kwargs):
        """Set value in cache"""
        key = self._generate_key(prefix, *args, **kwargs)
        ttl = ttl or self.default_ttl
        expiry = datetime.now() + timedelta(seconds=ttl)
        self.cache[key] = (value, expiry)
    
    def clear(self, prefix: Optional[str] = None):
        """Clear cache, optionally by prefix"""
        if prefix:
            # Clear all keys with this prefix (would need to track prefixes)
            keys_to_remove = [k for k in self.cache.keys() if k.startswith(prefix)]
            for key in keys_to_remove:
                del self.cache[key]
        else:
            self.cache.clear()
    
    def cleanup_expired(self):
        """Remove expired entries"""
        now = datetime.now()
        expired_keys = [
            key for key, (_, expiry) in self.cache.items()
            if now >= expiry
        ]
        for key in expired_keys:
            del self.cache[key]

# Global cache instance
cache = SimpleCache(default_ttl=300)  # 5 minutes

