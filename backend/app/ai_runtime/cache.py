"""CLINOVA AI — Deterministic AI Output Cache & Invalidation Engine.

Phase 10: Local AI Runtime Foundation & Safe Inference Architecture.
Caches validated AI outputs strictly keyed to source evidence fingerprints.
Enforces immediate cache invalidation when clinically meaningful case evidence changes.
"""

import hashlib
import json
import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class CacheEntry(BaseModel):
    """Immutable cached AI inference record."""
    cache_key: str
    case_id: str
    model_id: str
    model_version: str
    prompt_version: str
    source_fingerprint: str
    payload: Dict[str, Any]
    created_at_epoch: float = Field(default_factory=time.time)
    ttl_seconds: float = Field(default=3600.0)


class AICache:
    """In-memory deterministic cache with evidence-fingerprint invalidation."""

    def __init__(self, default_ttl_seconds: float = 3600.0):
        self.default_ttl = default_ttl_seconds
        self._store: Dict[str, CacheEntry] = {}

    @staticmethod
    def compute_source_fingerprint(evidence_items: list[Dict[str, Any]]) -> str:
        """Computes deterministic SHA-256 hash across sorted evidence records."""
        canonical_str = json.dumps(sorted(evidence_items, key=lambda x: str(x.get("id", ""))), sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    @staticmethod
    def generate_cache_key(
        case_id: str,
        task_name: str,
        prompt_version: str,
        model_id: str,
        model_version: str,
        source_fingerprint: str,
    ) -> str:
        """Constructs an immutable SHA-256 cache key."""
        raw_key = f"{case_id}:{task_name}:{prompt_version}:{model_id}:{model_version}:{source_fingerprint}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def get(
        self,
        case_id: str,
        task_name: str,
        prompt_version: str,
        model_id: str,
        model_version: str,
        current_source_fingerprint: str,
    ) -> Optional[Dict[str, Any]]:
        """Retrieves cached output only if fingerprint matches exactly and TTL has not expired."""
        key = self.generate_cache_key(
            case_id, task_name, prompt_version, model_id, model_version, current_source_fingerprint
        )
        entry = self._store.get(key)
        if entry is None:
            return None

        # Check TTL
        if time.time() - entry.created_at_epoch > entry.ttl_seconds:
            del self._store[key]
            return None

        # Check fingerprint match (stale invalidation check)
        if entry.source_fingerprint != current_source_fingerprint:
            del self._store[key]
            return None

        return entry.payload

    def set(
        self,
        case_id: str,
        task_name: str,
        prompt_version: str,
        model_id: str,
        model_version: str,
        source_fingerprint: str,
        payload: Dict[str, Any],
        ttl_seconds: Optional[float] = None,
    ):
        """Stores a validated inference in the cache."""
        key = self.generate_cache_key(
            case_id, task_name, prompt_version, model_id, model_version, source_fingerprint
        )
        self._store[key] = CacheEntry(
            cache_key=key,
            case_id=case_id,
            model_id=model_id,
            model_version=model_version,
            prompt_version=prompt_version,
            source_fingerprint=source_fingerprint,
            payload=payload,
            ttl_seconds=ttl_seconds or self.default_ttl,
        )

    def invalidate_case(self, case_id: str):
        """Invalidates all cached inferences for a specific case."""
        keys_to_delete = [k for k, v in self._store.items() if v.case_id == case_id]
        for k in keys_to_delete:
            del self._store[k]

    def clear(self):
        """Empties the cache."""
        self._store.clear()
