"""Contract tests for CTA Orange authored-graph helper state."""

from __future__ import annotations

from cta_kernel.ir import EdgeRef

from cta_orange.helpers import CTARef, GraphRegistry

SCOPE = {"dataset_id": "helper-tests", "slice_id": "all"}


def _ref(*, session_id: str, node_id: str, port: str = "raw_table") -> CTARef:
    """Construct a lightweight authored-edge reference for registry tests."""

    # Evidence identity is irrelevant to graph coordinates in these tests.
    return CTARef(
        session_id=session_id,
        evidence_id=f"evidence-{node_id}",
        type_id="RawTable",
        node_id=node_id,
        port=port,
        meta={},
    )


def test_compile_subgraph_uses_public_graphspec_01_and_authored_coordinates() -> None:
    """Compilation preserves authored facts without private scheduling authority."""

    # Arrange: author one LoadTSV feeding one BuildStringStore node.
    registry = GraphRegistry(
        profile_id="comhum_v0",
        scope=SCOPE,
        session_id="workspace-a",
    )
    registry.upsert_node("load", "LoadTSV", {"path": "fixture.tsv"})
    registry.upsert_node(
        "store",
        "BuildStringStore",
        {"string_col": "text", "source_id_cols": ["source"]},
    )
    registry.set_input("store", "raw_table", _ref(session_id="workspace-a", node_id="load"))

    # Act: compile only the target's present authored upstream closure.
    spec = registry.compile_subgraph("store")
    nodes = {node.node_id: node for node in spec.nodes}

    # Assert: public IR coordinates and session scope survive compilation.
    assert spec.schema_version == "0.1"
    assert spec.profile_id == "comhum_v0"
    assert spec.scope == SCOPE
    assert set(nodes) == {"load", "store"}
    assert nodes["store"].inputs["raw_table"] == EdgeRef(
        upstream_node="load",
        upstream_port="raw_table",
    )


def test_cross_workspace_reference_is_rejected_before_storage() -> None:
    """Authored edges cannot silently combine independent runtime workspaces."""

    # Arrange: create a target in one workspace and a ref from another.
    registry = GraphRegistry(
        profile_id="comhum_v0",
        scope=SCOPE,
        session_id="workspace-a",
    )
    registry.upsert_node("store", "BuildStringStore", {})
    foreign = _ref(session_id="workspace-b", node_id="load")

    # Act/Assert: the registry rejects the edge without mutating authored inputs.
    try:
        registry.set_input("store", "raw_table", foreign)
    except ValueError as exc:
        assert "workspace" in str(exc).lower() or "session" in str(exc).lower()
    else:
        raise AssertionError("cross-workspace reference was accepted")
    assert registry.inputs["store"] == {}


def test_remove_node_prunes_downstream_edges_and_clear_input_is_idempotent() -> None:
    """Widget deletion changes authored state without requiring history deletion."""

    # Arrange: author one dependency edge and exercise an absent clear first.
    registry = GraphRegistry(
        profile_id="comhum_v0",
        scope=SCOPE,
        session_id="workspace-a",
    )
    registry.upsert_node("load", "LoadTSV", {})
    registry.upsert_node("store", "BuildStringStore", {})
    registry.clear_input("store", "raw_table")
    registry.set_input("store", "raw_table", _ref(session_id="workspace-a", node_id="load"))

    # Act: deleting the upstream widget prunes authored downstream wiring.
    registry.remove_node("load")
    registry.clear_input("store", "raw_table")

    # Assert: the target remains authored but its removed dependency does not.
    assert "load" not in registry.nodes
    assert "store" in registry.nodes
    assert registry.inputs["store"] == {}


def test_target_anchoring_excludes_unrelated_under_supported_branch() -> None:
    """A valid upstream target is compilable despite an invalid sibling branch."""

    # Arrange: one executable load and one unrelated node missing its required input.
    registry = GraphRegistry(
        profile_id="comhum_v0",
        scope=SCOPE,
        session_id="workspace-a",
    )
    registry.upsert_node("load", "LoadTSV", {"path": "fixture.tsv"})
    registry.upsert_node(
        "broken_store",
        "BuildStringStore",
        {"string_col": "text", "source_id_cols": ["source"]},
    )

    # Act: derive each target independently from the mutable authored workspace.
    load_spec = registry.compile_subgraph("load")
    broken_spec = registry.compile_subgraph("broken_store")

    # Assert: each graph contains only the selected target's authored closure.
    assert [node.node_id for node in load_spec.nodes] == ["load"]
    assert [node.node_id for node in broken_spec.nodes] == ["broken_store"]
