"""
═══════════════════════════════════════════════════════════════════════════════
SAHOOL - Provider Configuration Database Service
خدمة قاعدة بيانات تكوين المزودين
═══════════════════════════════════════════════════════════════════════════════
"""

import json
import logging

import redis
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import ConfigVersion, Database, ProviderConfig

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# CACHE MANAGER
# ═══════════════════════════════════════════════════════════════════════════════


class CacheManager:
    """Redis cache manager for provider configurations"""

    def __init__(self, redis_url: str, cache_ttl: int = 300):
        """
        Initialize cache manager

        Args:
            redis_url: Redis connection URL
            cache_ttl: Cache TTL in seconds (default: 5 minutes)
        """
        self.cache_ttl = cache_ttl
        try:
            self.redis_client = redis.from_url(
                redis_url, decode_responses=True, socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.warning(f"Redis cache connection failed: {e}. Caching disabled.")
            self.redis_client = None

    def _get_key(self, tenant_id: str, provider_type: str | None = None) -> str:
        """Generate cache key"""
        if provider_type:
            return f"provider_config:{tenant_id}:{provider_type}"
        return f"provider_config:{tenant_id}:all"

    def get(self, tenant_id: str, provider_type: str | None = None) -> dict | None:
        """Get cached configuration"""
        if not self.redis_client:
            return None

        try:
            key = self._get_key(tenant_id, provider_type)
            data = self.redis_client.get(key)
            if data:
                logger.debug(f"Cache hit for {key}")
                return json.loads(data)
            logger.debug(f"Cache miss for {key}")
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(self, tenant_id: str, data: dict, provider_type: str | None = None) -> bool:
        """Set cached configuration"""
        if not self.redis_client:
            return False

        try:
            key = self._get_key(tenant_id, provider_type)
            self.redis_client.setex(key, self.cache_ttl, json.dumps(data))
            logger.debug(f"Cache set for {key}")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def invalidate(self, tenant_id: str, provider_type: str | None = None):
        """Invalidate cache for tenant"""
        if not self.redis_client:
            return

        try:
            if provider_type:
                # Invalidate specific provider type
                key = self._get_key(tenant_id, provider_type)
                self.redis_client.delete(key)
            else:
                # Invalidate all provider types for tenant
                pattern = f"provider_config:{tenant_id}:*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            logger.debug(f"Cache invalidated for tenant {tenant_id}")
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE SERVICE
# ═══════════════════════════════════════════════════════════════════════════════


class ProviderConfigService:
    """Service for managing provider configurations with database and cache"""

    def __init__(self, database: Database, cache: CacheManager):
        self.db = database
        self.cache = cache

    # ─────────────────────────────────────────────────────────────────────────
    # CREATE
    # ─────────────────────────────────────────────────────────────────────────

    def create_config(
        self,
        session: Session,
        tenant_id: str,
        provider_type: str,
        provider_name: str,
        api_key: str | None = None,
        api_secret: str | None = None,
        priority: str = "primary",
        enabled: bool = True,
        config_data: dict | None = None,
        created_by: str | None = None,
    ) -> ProviderConfig:
        """Create new provider configuration"""
        try:
            config = ProviderConfig(
                tenant_id=tenant_id,
                provider_type=provider_type,
                provider_name=provider_name,
                api_key=api_key,
                api_secret=api_secret,
                priority=priority,
                enabled=enabled,
                config_data=config_data,
                created_by=created_by,
            )
            session.add(config)
            session.commit()
            session.refresh(config)

            # Invalidate cache
            self.cache.invalidate(tenant_id, provider_type)

            logger.info(f"Created config for tenant {tenant_id}: {provider_type}/{provider_name}")
            return config

        except IntegrityError:
            session.rollback()
            logger.error(
                f"Duplicate config: tenant={tenant_id}, type={provider_type}, name={provider_name}"
            )
            raise ValueError(f"Configuration already exists for {provider_type}/{provider_name}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating config: {e}")
            raise

    # ─────────────────────────────────────────────────────────────────────────
    # READ
    # ─────────────────────────────────────────────────────────────────────────

    def get_tenant_configs(
        self, session: Session, tenant_id: str, provider_type: str | None = None
    ) -> list[ProviderConfig]:
        """Get all provider configurations for a tenant"""
        # Check cache first
        cached = self.cache.get(tenant_id, provider_type)
        if cached:
            # Return from cache (need to convert back to models)
            return cached

        # Query database
        query = session.query(ProviderConfig).filter(ProviderConfig.tenant_id == tenant_id)

        if provider_type:
            query = query.filter(ProviderConfig.provider_type == provider_type)

        configs = query.all()

        # Cache results
        configs_dict = [config.to_dict() for config in configs]
        self.cache.set(tenant_id, configs_dict, provider_type)

        return configs

    def get_config_by_name(
        self, session: Session, tenant_id: str, provider_type: str, provider_name: str
    ) -> ProviderConfig | None:
        """Get specific provider configuration"""
        return (
            session.query(ProviderConfig)
            .filter(
                ProviderConfig.tenant_id == tenant_id,
                ProviderConfig.provider_type == provider_type,
                ProviderConfig.provider_name == provider_name,
            )
            .first()
        )

    def get_enabled_providers(
        self, session: Session, tenant_id: str, provider_type: str
    ) -> list[ProviderConfig]:
        """Get all enabled providers of a specific type for failover"""
        return (
            session.query(ProviderConfig)
            .filter(
                ProviderConfig.tenant_id == tenant_id,
                ProviderConfig.provider_type == provider_type,
                ProviderConfig.enabled == True,
            )
            .order_by(
                # Order by priority (primary first)
                ProviderConfig.priority
            )
            .all()
        )

    # ─────────────────────────────────────────────────────────────────────────
    # UPDATE
    # ─────────────────────────────────────────────────────────────────────────

    def update_config(
        self,
        session: Session,
        tenant_id: str,
        provider_type: str,
        provider_name: str,
        api_key: str | None = None,
        api_secret: str | None = None,
        priority: str | None = None,
        enabled: bool | None = None,
        config_data: dict | None = None,
        updated_by: str | None = None,
    ) -> ProviderConfig | None:
        """Update provider configuration"""
        try:
            config = self.get_config_by_name(session, tenant_id, provider_type, provider_name)
            if not config:
                return None

            # Update fields
            if api_key is not None:
                config.api_key = api_key
            if api_secret is not None:
                config.api_secret = api_secret
            if priority is not None:
                config.priority = priority
            if enabled is not None:
                config.enabled = enabled
            if config_data is not None:
                config.config_data = config_data
            if updated_by is not None:
                config.updated_by = updated_by

            session.commit()
            session.refresh(config)

            # Invalidate cache
            self.cache.invalidate(tenant_id, provider_type)

            logger.info(f"Updated config for tenant {tenant_id}: {provider_type}/{provider_name}")
            return config

        except Exception as e:
            session.rollback()
            logger.error(f"Error updating config: {e}")
            raise

    # ─────────────────────────────────────────────────────────────────────────
    # DELETE
    # ─────────────────────────────────────────────────────────────────────────

    def delete_config(
        self, session: Session, tenant_id: str, provider_type: str, provider_name: str
    ) -> bool:
        """Delete provider configuration"""
        try:
            config = self.get_config_by_name(session, tenant_id, provider_type, provider_name)
            if not config:
                return False

            session.delete(config)
            session.commit()

            # Invalidate cache
            self.cache.invalidate(tenant_id, provider_type)

            logger.info(f"Deleted config for tenant {tenant_id}: {provider_type}/{provider_name}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting config: {e}")
            raise

    # ─────────────────────────────────────────────────────────────────────────
    # VERSION HISTORY
    # ─────────────────────────────────────────────────────────────────────────

    def get_config_history(
        self,
        session: Session,
        tenant_id: str,
        provider_type: str | None = None,
        limit: int = 100,
    ) -> list[ConfigVersion]:
        """Get configuration change history"""
        query = session.query(ConfigVersion).filter(ConfigVersion.tenant_id == tenant_id)

        if provider_type:
            query = query.filter(ConfigVersion.provider_type == provider_type)

        return query.order_by(ConfigVersion.changed_at.desc()).limit(limit).all()

    def get_config_version(
        self, session: Session, config_id: str, version: int
    ) -> ConfigVersion | None:
        """Get specific version of a configuration"""
        return (
            session.query(ConfigVersion)
            .filter(ConfigVersion.config_id == config_id, ConfigVersion.version == version)
            .first()
        )

    def rollback_to_version(
        self, session: Session, config_id: str, version: int, updated_by: str | None = None
    ) -> ProviderConfig | None:
        """Rollback configuration to a specific version"""
        try:
            # Get the version to rollback to
            version_record = self.get_config_version(session, config_id, version)
            if not version_record:
                return None

            # Get current config
            config = session.query(ProviderConfig).filter(ProviderConfig.id == config_id).first()
            if not config:
                return None

            # Restore values from version
            config.api_key = version_record.api_key
            config.api_secret = version_record.api_secret
            config.priority = version_record.priority
            config.enabled = version_record.enabled
            config.config_data = version_record.config_data
            config.updated_by = updated_by

            session.commit()
            session.refresh(config)

            # Invalidate cache
            self.cache.invalidate(config.tenant_id, config.provider_type)

            logger.info(f"Rolled back config {config_id} to version {version}")
            return config

        except Exception as e:
            session.rollback()
            logger.error(f"Error rolling back config: {e}")
            raise
