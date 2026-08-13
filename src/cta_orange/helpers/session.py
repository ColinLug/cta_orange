"""Thin CTA Orange workspace façade over the supported persistent kernel runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping
from uuid import uuid4

from cta_kernel import KernelRuntime, RunResult
from cta_kernel.errors import OutputResolutionError

from cta_orange.helpers.ref import CTARef
from cta_orange.helpers.registry import GraphRegistry


@dataclass
class CTASession:
    """Group Orange-authored graph state with one public persistent runtime."""

    profile_id: str
    scope: dict[str, Any]
    session_id: str
    runtime: KernelRuntime
    registry: GraphRegistry
    _latest_results: dict[str, RunResult] = field(default_factory=dict, repr=False)

    @classmethod
    def create(
        cls,
        *,
        profile_id: str,
        scope: Mapping[str, Any],
        session_id: str | None = None,
    ) -> CTASession:
        """Create one independent Orange workspace for a supported profile."""

        # Keep workspace identity injectable for deterministic tests and diagnostics.
        selected_id = session_id or uuid4().hex
        runtime = KernelRuntime.for_profile(profile_id)

        # Orange owns authored graph state; the kernel owns all execution state.
        registry = GraphRegistry(
            profile_id=profile_id,
            scope=dict(scope),
            session_id=selected_id,
        )
        return cls(
            profile_id=profile_id,
            scope=dict(scope),
            session_id=selected_id,
            runtime=runtime,
            registry=registry,
        )

    def ensure_computed(self, target_node_id: str) -> RunResult:
        """Compile and execute the target-anchored authored subgraph."""

        # The public runtime performs formal checking, scheduling, caching, and execution.
        spec = self.registry.compile_subgraph(target_node_id)
        result = self.runtime.run(spec)

        # Retain only public run results needed to resolve later Orange output refs.
        for node in result.spec.nodes:
            self._latest_results[node.node_id] = result
        return result

    def output_ref(self, node_id: str, port: str) -> CTARef:
        """Return an Orange transport reference for the latest computed output."""

        # Resolve through the retained public RunResult rather than mutable kernel internals.
        result = self._latest_results.get(node_id)
        if result is None:
            raise OutputResolutionError(
                f"No completed run is available for node {node_id!r}",
                context={"node_id": node_id, "port": port},
            )
        evidence = result.output(node_id, port)

        # Carry evidence identity plus authored coordinates across Orange signals.
        return CTARef.from_evidence(
            session_id=self.session_id,
            node_id=node_id,
            port=port,
            evidence=evidence,
        )

    def evidence(self, ref: CTARef) -> Any:
        """Dereference a local CTARef through the public runtime evidence API."""

        # Workspace mismatch is an Orange transport error and precedes kernel lookup.
        if ref.session_id != self.session_id:
            raise ValueError(
                f"CTARef workspace mismatch: ref={ref.session_id!r}, session={self.session_id!r}"
            )
        return self.runtime.evidence(ref.evidence_id)

    def all_evidence(self) -> tuple[Any, ...]:
        """Return all evidence accumulated by this workspace's public runtime."""

        # Preserve the runtime's intentionally unspecified evidence ordering.
        return self.runtime.all_evidence()
