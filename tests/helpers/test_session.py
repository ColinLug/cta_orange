"""Contract tests for the thin CTA Orange session/runtime adapter."""

from __future__ import annotations

from pathlib import Path

import pytest
from cta_kernel import KernelRuntime, RunResult
from cta_kernel.errors import AdmissibilityError, OutputResolutionError

from cta_orange.helpers import CTARef, CTASession

FIXTURE = Path(__file__).parents[1] / "data" / "helper_runtime_fixture.tsv"
SCOPE = {"dataset_id": "helper-tests", "slice_id": "all"}


def _session() -> CTASession:
    """Create one deterministic helper workspace around the public runtime."""

    # A fixed id makes cross-workspace behavior and failure messages inspectable.
    return CTASession.create(
        profile_id="comhum_v0",
        scope=SCOPE,
        session_id="workspace-a",
    )


def _author_load(session: CTASession, node_id: str = "load") -> None:
    """Author one valid LoadTSV node in a helper workspace."""

    # Keep execution fixtures minimal so these tests isolate helper contracts.
    session.registry.upsert_node(
        node_id,
        "LoadTSV",
        {"path": str(FIXTURE)},
    )


def test_session_is_thin_workspace_facade_over_one_public_runtime() -> None:
    """CTASession groups Orange state without re-exposing kernel internals."""

    # Arrange/Act: create the selected retained session design.
    session = _session()

    # Assert: one public runtime is visible and legacy runtime machinery is not.
    assert isinstance(session.runtime, KernelRuntime)
    assert session.registry.session_id == session.session_id
    assert not hasattr(session, "store")
    assert not hasattr(session, "cache")
    assert not hasattr(session, "executor")


def test_execution_returns_runresult_and_resolves_ref_through_public_evidence() -> None:
    """Incremental execution and dereference use supported runtime objects only."""

    # Arrange: author one executable target.
    session = _session()
    _author_load(session)

    # Act: compute, obtain an Orange transport ref, and dereference it.
    result = session.ensure_computed("load")
    ref = session.output_ref("load", "raw_table")
    evidence = session.evidence(ref)

    # Assert: result coordinates, ref identity, and public evidence agree.
    assert isinstance(result, RunResult)
    assert result.output_id("load", "raw_table") == ref.evidence_id
    assert evidence == session.runtime.evidence(ref.evidence_id)
    assert evidence.type_id == "RawTable"


def test_repeated_target_execution_reuses_runtime_cache_and_output_resolution() -> None:
    """Successive widget commits share persistent kernel cache and evidence history."""

    # Arrange: author one target and execute it once through the shared runtime.
    session = _session()
    _author_load(session)
    first = session.ensure_computed("load")

    # Act: execute the unchanged target again and resolve its output afterward.
    second = session.ensure_computed("load")
    ref = session.output_ref("load", "raw_table")

    # Assert: the second run is a cache hit and retained output remains inspectable.
    assert "load" in first.run_log.computed
    assert second.run_log.computed == set()
    assert second.run_log.cache_hits == {"load"}
    assert session.evidence(ref) == second.output("load", "raw_table")


def test_node_removal_does_not_delete_accumulated_runtime_evidence() -> None:
    """Authored graph deletion is distinct from persistent session evidence history."""

    # Arrange: materialize evidence before deleting its authored producer.
    session = _session()
    _author_load(session)
    session.ensure_computed("load")
    ref = session.output_ref("load", "raw_table")
    before = session.evidence(ref)

    # Act: remove only the authored node from the Orange-owned registry.
    session.registry.remove_node("load")
    after = session.evidence(ref)

    # Assert: authored state is gone while public runtime history survives.
    assert "load" not in session.registry.nodes
    assert after == before
    assert after in session.all_evidence()


def test_kernel_owns_admissibility_for_under_supported_compiled_target() -> None:
    """Helpers compile incomplete authored work and let the kernel reject it."""

    # Arrange: author a node with valid params but omit its required raw_table input.
    session = _session()
    session.registry.upsert_node(
        "broken_store",
        "BuildStringStore",
        {"string_col": "text", "source_id_cols": ["source"]},
    )

    # Act/Assert: execution reaches the public kernel admissibility boundary.
    with pytest.raises(AdmissibilityError) as exc_info:
        session.ensure_computed("broken_store")

    violations = exc_info.value.context["violations"]
    assert any(violation.node_id == "broken_store" for violation in violations)


def test_unrelated_invalid_branch_does_not_block_valid_target_execution() -> None:
    """Target-anchored execution ignores invalid authored branches outside the closure."""

    # Arrange: author one valid target plus one unrelated under-supported node.
    session = _session()
    _author_load(session)
    session.registry.upsert_node(
        "broken_store",
        "BuildStringStore",
        {"string_col": "text", "source_id_cols": ["source"]},
    )

    # Act: execute only the independently valid upstream target.
    result = session.ensure_computed("load")

    # Assert: the selected closure executes without helper-wide validity rejection.
    assert result.output("load", "raw_table").type_id == "RawTable"
    assert {node.node_id for node in result.spec.nodes} == {"load"}


def test_unknown_and_cross_workspace_evidence_use_clear_public_boundaries() -> None:
    """Dereference failures distinguish kernel absence from Orange workspace mismatch."""

    # Arrange: create one local ref with an absent id and one foreign-workspace ref.
    session = _session()
    missing = CTARef(
        session_id=session.session_id,
        evidence_id="missing-evidence",
        type_id="RawTable",
        node_id="load",
        port="raw_table",
        meta={},
    )
    foreign = CTARef(
        session_id="workspace-b",
        evidence_id="missing-evidence",
        type_id="RawTable",
        node_id="load",
        port="raw_table",
        meta={},
    )

    # Assert: local absence preserves the kernel's typed resolution failure.
    with pytest.raises(OutputResolutionError):
        session.evidence(missing)

    # Assert: foreign references fail at the Orange workspace boundary first.
    with pytest.raises(ValueError) as exc_info:
        session.evidence(foreign)
    assert "workspace" in str(exc_info.value).lower() or "session" in str(exc_info.value).lower()
