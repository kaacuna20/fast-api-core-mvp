import aioredis
from config.settings import Settings
from typing import Optional


class CacheManager:
    """Manager para manejar la caché con Redis"""
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
    
    async def connect(self):
        """Conecta al servidor Redis"""
        self.redis = await aioredis.from_url(Settings.CACHE_REDIS_URL)
    
    async def disconnect(self):
        """Desconecta del servidor Redis"""
        if self.redis:
            await self.redis.close()
    
    async def set(self, key: str, value: str, expire: int = Settings.CACHE_EXPIRE_SECONDS):
        """Establece un valor en la caché con una expiración"""
        if self.redis:
            await self.redis.set(key, value, ex=expire)
    
    async def get(self, key: str) -> Optional[str]:
        """Obtiene un valor de la caché"""
        if self.redis:
            value = await self.redis.get(key)
            return value.decode() if value else None
        return None
    
    async def delete(self, key: str):
        """Elimina un valor de la caché"""
        if self.redis:
            await self.redis.delete(key)
    

