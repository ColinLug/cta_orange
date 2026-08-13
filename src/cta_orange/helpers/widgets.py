"""Shared Orange lifecycle logic for CTA kernel-backed widgets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from cta_orange.helpers.ref import CTARef
from cta_orange.helpers.session import CTASession

# Keep helper imports usable in headless tests and non-Orange environments.
try:
    from Orange.widgets.widget import OWWidget
except ImportError:
    OWWidget = object  # type: ignore[assignment,misc]
    ORANGE_AVAILABLE = False
else:
    ORANGE_AVAILABLE = True


@dataclass
class KernelWidgetLogic:
    """Coordinate common authored-graph updates without owning kernel semantics."""

    op_id: str
    out_port: str
    node_id: str = ""
    session: CTASession | None = None

    def __post_init__(self) -> None:
        """Assign a stable readable node id when the widget provides none."""

        # The id is authored-graph identity only; it has no kernel scheduling role.
        if not self.node_id:
            self.node_id = f"{self.op_id.lower()}_{uuid4().hex[:8]}"

    def _params(self) -> dict[str, Any]:
        """Return JSON-friendly operator parameters supplied by the widget."""

        raise NotImplementedError

    def _collect_inputs(self) -> dict[str, CTARef | None]:
        """Return current authored input wiring supplied by the widget."""

        raise NotImplementedError

    def _is_ready(self, inputs: dict[str, CTARef | None]) -> bool:
        """Return whether the widget has all interaction-level inputs it declares."""

        # This is UI readiness only; kernel admissibility remains authoritative.
        return all(ref is not None for ref in inputs.values())

    def _send_none(self) -> None:
        """Clear widget outputs when interaction-level inputs are incomplete."""

        raise NotImplementedError

    def _send_ref(self, ref: CTARef) -> Any:
        """Emit one materialized output reference downstream."""

        raise NotImplementedError

    def commit(self) -> Any:
        """Mirror authored state, execute the target when ready, and emit its ref."""

        # A widget without a workspace cannot author or execute a kernel target.
        if self.session is None:
            self._send_none()
            return None
        inputs = self._collect_inputs()

        # Record local authored facts before considering interaction-level readiness.
        self.session.registry.upsert_node(self.node_id, self.op_id, self._params())
        for input_name, ref in inputs.items():
            if ref is None:
                self.session.registry.clear_input(self.node_id, input_name)
            else:
                self.session.registry.set_input(self.node_id, input_name, ref)

        # Incomplete UI wiring propagates absence without duplicating admissibility.
        if not self._is_ready(inputs):
            self._send_none()
            return None
        self.session.ensure_computed(self.node_id)

        # Output transport is resolved only after the public runtime completes.
        ref = self.session.output_ref(self.node_id, self.out_port)
        return self._send_ref(ref)

    def delete(self) -> None:
        """Mirror widget deletion into the authored registry only."""

        # Runtime evidence history intentionally survives authored-node removal.
        if self.session is not None:
            self.session.registry.remove_node(self.node_id)


class _OWCTAKernelMixin:
    """Implement shared Orange-facing hooks independently of the OWWidget base."""

    op_id: str = ""
    out_port: str = ""

    def __init__(self) -> None:
        """Create the widget and its pure-Python lifecycle helper."""

        # Keep failure explicit when the package is imported without Orange.
        if not ORANGE_AVAILABLE:
            raise ImportError("Orange is required to instantiate OWCTAKernelBase")
        super().__init__()
        self._logic = KernelWidgetLogic(op_id=self.op_id, out_port=self.out_port)

    def _params(self) -> dict[str, Any]:
        """Return operator parameters; concrete widgets override this hook."""

        return {}

    def _collect_inputs(self) -> dict[str, CTARef | None]:
        """Return authored inputs; concrete widgets override this hook."""

        return {}

    def _send_none(self) -> None:
        """Clear concrete widget outputs."""

        return None

    def _send_ref(self, ref: CTARef) -> Any:
        """Emit a concrete widget output reference."""

        return None

    def sendData(self) -> None:
        """Retain the legacy subclass hook used by current CTA Orange widgets."""

        return None

    def handleNewSignals(self) -> Any:
        """Bind concrete hooks and execute one coalesced widget commit."""

        # Bind widget implementations into the independently testable logic object.
        self._logic._params = self._params  # type: ignore[method-assign]
        self._logic._collect_inputs = self._collect_inputs  # type: ignore[method-assign]
        self._logic._send_none = self._send_none  # type: ignore[method-assign]
        self._logic._send_ref = self._send_ref  # type: ignore[method-assign]

        # Preserve current Orange failure behavior while clearing stale outputs.
        try:
            return self._logic.commit()
        except Exception as exc:  # noqa: BLE001
            self.error(f"Computation failed: {exc}")
            self._send_none()
            return None

    def onDeleteWidget(self) -> None:
        """Remove authored state before delegating widget deletion to Orange."""

        # Deletion affects authored graph state but not accumulated runtime evidence.
        self._logic.delete()
        super().onDeleteWidget()


if ORANGE_AVAILABLE:

    class OWCTAKernelBase(_OWCTAKernelMixin, OWWidget, openclass=True):
        """Orange base widget delegating lifecycle work to KernelWidgetLogic."""

else:

    class OWCTAKernelBase(_OWCTAKernelMixin):
        """Headless placeholder that fails only if callers try to instantiate it."""
