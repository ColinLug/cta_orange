"""Mutable authored-graph state for incremental CTA Orange execution."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass, field
from typing import Any

from cta_kernel.ir import EdgeRef, GraphSpec, NodeSpec

from cta_orange.helpers.ref import CTARef


@dataclass(frozen=True)
class NodeRecord:
    """Record the authored operator identity and parameters of one widget node."""

    node_id: str
    op_id: str
    params: dict[str, Any]


@dataclass
class GraphRegistry:
    """Own mutable Orange-authored nodes and edges for one workspace."""

    profile_id: str
    scope: dict[str, Any]
    session_id: str
    nodes: MutableMapping[str, NodeRecord] = field(default_factory=dict)
    inputs: MutableMapping[str, MutableMapping[str, CTARef]] = field(default_factory=dict)

    def upsert_node(self, node_id: str, op_id: str, params: Mapping[str, Any]) -> None:
        """Insert or replace one authored node without validating kernel semantics."""

        # Preserve authored facts while ensuring every node has an input mapping.
        self.nodes[node_id] = NodeRecord(node_id=node_id, op_id=op_id, params=dict(params))
        self.inputs.setdefault(node_id, {})

    def set_input(self, node_id: str, input_name: str, ref: CTARef) -> None:
        """Set one authored input edge after enforcing workspace identity."""

        # Reject missing targets and cross-workspace wiring before mutating state.
        if node_id not in self.nodes:
            raise KeyError(f"Unknown node_id={node_id!r} (cannot set input)")
        if ref.session_id != self.session_id:
            raise ValueError(
                f"CTARef workspace mismatch: ref={ref.session_id!r}, registry={self.session_id!r}"
            )

        # Store the transport reference; compilation later uses only its coordinates.
        self.inputs.setdefault(node_id, {})[input_name] = ref

    def clear_input(self, node_id: str, input_name: str) -> None:
        """Clear one authored input edge idempotently."""

        # Orange disconnect notifications may arrive after prior cleanup.
        if node_id in self.inputs:
            self.inputs[node_id].pop(input_name, None)

    def remove_node(self, node_id: str) -> None:
        """Remove one authored node and prune every downstream edge to it."""

        # Delete the node itself without touching runtime evidence history.
        self.nodes.pop(node_id, None)
        self.inputs.pop(node_id, None)

        # Remove dangling authored edges left in downstream widget records.
        for input_map in self.inputs.values():
            stale = [name for name, ref in input_map.items() if ref.node_id == node_id]
            for name in stale:
                input_map.pop(name, None)

    def compile_subgraph(self, target_node_id: str) -> GraphSpec:
        """Compile the target and its present authored upstream closure."""

        # Resolve only authored connectivity; kernel admissibility owns completeness.
        needed = self._upstream_closure(target_node_id)
        node_specs: list[NodeSpec] = []

        # Preserve registry insertion order rather than reimplement kernel scheduling.
        for node_id, record in self.nodes.items():
            if node_id not in needed:
                continue
            edges = {
                input_name: EdgeRef(upstream_node=ref.node_id, upstream_port=ref.port)
                for input_name, ref in self.inputs.get(node_id, {}).items()
            }
            node_specs.append(
                NodeSpec(
                    node_id=record.node_id,
                    op_id=record.op_id,
                    params=dict(record.params),
                    inputs=edges,
                )
            )

        # Emit the released GraphSpec schema and workspace scope verbatim.
        return GraphSpec(
            schema_version="0.1",
            profile_id=self.profile_id,
            scope=dict(self.scope),
            nodes=node_specs,
        )

    def _upstream_closure(self, target_node_id: str) -> set[str]:
        """Return node ids reachable upstream through present authored edges."""

        # A missing target is an Orange authoring error, not a kernel graph condition.
        if target_node_id not in self.nodes:
            raise KeyError(f"Unknown node_id={target_node_id!r} (cannot compile subgraph)")
        needed: set[str] = set()
        stack = [target_node_id]

        # Follow only stored authored references and reject dangling coordinates.
        while stack:
            node_id = stack.pop()
            if node_id in needed:
                continue
            if node_id not in self.nodes:
                raise KeyError(f"Referenced node {node_id!r} is absent from the registry")
            needed.add(node_id)
            stack.extend(ref.node_id for ref in self.inputs.get(node_id, {}).values())

        return needed
