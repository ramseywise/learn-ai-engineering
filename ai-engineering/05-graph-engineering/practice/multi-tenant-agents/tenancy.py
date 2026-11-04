"""Per-tenant configuration: validated on the way in, versioned per tenant, rolled out and rolled back per tenant.
NaiveConfigStore beside it is the failure to compare with: no validation, live on save, one fleet-wide undo."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, replace
from pathlib import Path
from types import SimpleNamespace

TOOL_CATALOG = {"lookup_record", "create_ticket", "issue_refund", "book_collection"}
TENANT_IDS = ("larkspur-clinic", "tallow-legal", "pinwheel-retail", "ferrous-freight")
KNOWN_SCOPES = {"shared/product"} | {f"{t}/{s}" for t in TENANT_IDS for s in ("policies", "internal")}
MODEL_ALIASES = {"support-model@v1", "support-model@v2"}
REQUIRED = {"tenant_id", "vertical", "system_prompt", "rubric", "tools", "knowledge_scopes", "model_alias",
            "monthly_tokens", "max_tokens", "rate_per_s", "burst", "queue_weight"}


class ConfigError(ValueError):
    def __init__(self, tenant: str, errors: list[str]):
        super().__init__(f"{tenant}: " + "; ".join(errors))
        self.errors = errors


class UnknownTenant(KeyError):
    """No configuration means no service. There is no default tenant to fall back to."""


@dataclass(frozen=True)
class TenantConfig:
    tenant_id: str
    vertical: str
    system_prompt: str
    rubric: dict
    tools: tuple[str, ...]
    knowledge_scopes: tuple[str, ...]
    model_alias: str
    monthly_tokens: int
    max_tokens: int
    rate_per_s: float
    burst: int
    queue_weight: int
    version: int = 0  # assigned by the store, so an author can't claim one


def validate_config(raw: dict) -> TenantConfig:
    """Report key problems first, then every value problem at once, and never fill a gap with a default."""
    tenant = str(raw.get("tenant_id", "?"))
    errors = [f"missing {k}" for k in sorted(REQUIRED - raw.keys())]
    errors += [f"unknown key {k}" for k in sorted(raw.keys() - REQUIRED)]  # a typo must not silently mean "unset"
    if errors:
        raise ConfigError(tenant, errors)
    if tenant not in TENANT_IDS:
        errors.append(f"unknown tenant {tenant}")
    if not raw["system_prompt"].strip():
        errors.append("empty system_prompt")
    errors += [f"unknown tool {t}" for t in raw["tools"] if t not in TOOL_CATALOG]
    for scope in raw["knowledge_scopes"]:
        if scope not in KNOWN_SCOPES:
            errors.append(f"unknown scope {scope}")
        elif scope.split("/")[0] not in (tenant, "shared"):
            errors.append(f"scope {scope} belongs to another tenant")
    if not raw["knowledge_scopes"]:
        errors.append("no knowledge scopes")
    if raw["model_alias"] not in MODEL_ALIASES:
        errors.append(f"unknown model alias {raw['model_alias']}")
    for key in ("monthly_tokens", "max_tokens", "burst", "queue_weight"):
        if not isinstance(raw[key], int) or raw[key] <= 0:
            errors.append(f"{key} must be a positive integer")
    if not raw["rate_per_s"] > 0:
        errors.append("rate_per_s must be positive")
    rubric = raw["rubric"]
    criteria = rubric.get("criteria", [])
    if sum(c.get("weight", 0) for c in criteria) != 100:
        errors.append("rubric weights must sum to 100")
    if not 0 < rubric.get("min_score", 0) <= 100:
        errors.append("rubric min_score must be in 1..100")
    for c in criteria:
        if c.get("kind") not in ("cites", "contains") or (c.get("kind") == "contains" and not c.get("text")):
            errors.append(f"bad rubric criterion {c.get('name', '?')}")
    if errors:
        raise ConfigError(tenant, errors)
    return TenantConfig(**{**raw, "tools": tuple(raw["tools"]), "knowledge_scopes": tuple(raw["knowledge_scopes"])})


def score_answer(cfg, answer: str, retrieved_ids: list[str]) -> int:
    """Deterministic: code decides whether the citation is real, not the model that wrote it."""
    score = 0
    for c in cfg.rubric["criteria"]:
        if c["kind"] == "contains":
            met = c["text"].lower() in answer.lower()
        else:
            met = bool(set(re.findall(r"\[([\w-]+)\]", answer)) & set(retrieved_ids))
        score += c["weight"] if met else 0
    return score


def _bucket(tenant: str, version: int, run_id: str) -> int:
    # sha256 rather than hash(): Python randomises str hashes per process, which would reshuffle the canary.
    return int(hashlib.sha256(f"{tenant}:{version}:{run_id}".encode()).hexdigest(), 16) % 100


class ConfigStore:
    """Append-only versions per tenant. Every operation names one tenant and can only move that tenant."""

    def __init__(self):
        self._versions: dict[str, list[TenantConfig]] = {}
        self._stable: dict[str, list[int]] = {}  # the stack of stable versions, newest last
        self._canary: dict[str, tuple[int, int]] = {}

    def propose(self, raw: dict) -> int:
        cfg = validate_config(raw)
        versions = self._versions.setdefault(cfg.tenant_id, [])
        versions.append(replace(cfg, version=len(versions) + 1))
        if len(versions) == 1:  # the first version has nothing to canary against
            self._stable[cfg.tenant_id] = [1]
        return len(versions)

    def start_canary(self, tenant: str, version: int, percent: int) -> None:
        if not 0 < percent <= 100 or not 1 <= version <= len(self._versions[tenant]):
            raise ValueError(f"bad canary {version} at {percent}%")
        self._canary[tenant] = (version, percent)

    def promote(self, tenant: str) -> None:
        version, _ = self._canary.pop(tenant)
        self._stable[tenant].append(version)

    def rollback(self, tenant: str) -> int:
        """Abandon a canary if there is one, else return to the previous stable version."""
        if tenant in self._canary:
            del self._canary[tenant]
        elif len(self._stable[tenant]) > 1:
            self._stable[tenant].pop()
        return self._stable[tenant][-1]

    def resolve(self, tenant: str, run_id: str) -> TenantConfig:
        """A run calls this once and keeps the answer, so a rollback never changes a run halfway through."""
        if tenant not in self._versions:
            raise UnknownTenant(tenant)
        if tenant in self._canary:
            version, percent = self._canary[tenant]
            if _bucket(tenant, version, run_id) < percent:
                return self._versions[tenant][version - 1]
        return self._versions[tenant][self._stable[tenant][-1] - 1]

    def stable_version(self, tenant: str) -> int:
        return self._stable[tenant][-1]

    def get(self, tenant: str) -> TenantConfig:
        return self._versions[tenant][self.stable_version(tenant) - 1]


class NaiveConfigStore:
    """One dict of raw config, live the moment it is saved, with a fleet-wide snapshot as the only undo."""

    def __init__(self):
        self._live: dict[str, dict] = {}
        self._snapshots: list[dict[str, dict]] = []

    def propose(self, raw: dict) -> int:
        self._snapshots.append({k: dict(v) for k, v in self._live.items()})
        self._live[raw["tenant_id"]] = dict(raw)
        return len(self._snapshots)

    def start_canary(self, tenant: str, version: int, percent: int) -> None:
        pass  # it was already live for everyone

    def promote(self, tenant: str) -> None:
        pass

    def rollback(self, tenant: str) -> int:
        self._live = self._snapshots.pop()  # tenant is ignored: the undo restores everybody
        return len(self._snapshots)

    def resolve(self, tenant: str, run_id: str):
        raw = self._live.get(tenant) or next(iter(self._live.values()))  # falls back to whichever tenant came first
        return SimpleNamespace(**raw, version=len(self._snapshots))

    def stable_version(self, tenant: str) -> int:
        return len(self._snapshots)

    def get(self, tenant: str):
        return self.resolve(tenant, "")


def load_raw_configs() -> list[dict]:
    return json.loads((Path(__file__).parent / "tenants.json").read_text())


def load_store(store=None):
    store = store if store is not None else ConfigStore()
    for raw in load_raw_configs():
        store.propose(raw)
    return store
