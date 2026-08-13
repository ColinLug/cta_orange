"""Lightweight references exchanged between CTA Orange widgets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class CTARef:
    """Reference one materialized kernel evidence object in an Orange workspace."""

    session_id: str
    evidence_id: str
    type_id: str
    node_id: str
    port: str
    meta: dict[str, Any]

    @classmethod
    def from_evidence(
        cls,
        *,
        session_id: str,
        node_id: str,
        port: str,
        evidence: Any,
        meta: Mapping[str, Any] | None = None,
    ) -> CTARef:
        """Construct a reference from a public kernel evidence result."""

        # Keep only the stable public evidence identity needed for transport.
        return cls(
            session_id=session_id,
            evidence_id=evidence.evidence_id,
            type_id=evidence.type_id,
            node_id=node_id,
            port=port,
            meta=dict(meta or {}),
        )
