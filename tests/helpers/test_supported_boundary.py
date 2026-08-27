"""Static contract tests for the CTA Orange helper/kernel dependency boundary."""

from __future__ import annotations

import ast
from pathlib import Path

HELPERS = Path("src/cta_orange/helpers")
PRIVATE_KERNEL_MODULES = {
    "cta_kernel.runtime.bootstrap",
    "cta_kernel.runtime.cache",
    "cta_kernel.runtime.executor",
    "cta_kernel.runtime.evidence",
    "cta_kernel.runtime.registry",
    "cta_kernel.runtime.resolve",
    "cta_kernel.runtime.scheduler",
}


def test_helpers_do_not_import_private_kernel_runtime_services() -> None:
    """Orange helpers depend only on the released kernel's supported namespaces."""

    # Arrange: collect every Python module in the migrated helper package.
    paths = sorted(HELPERS.rglob("*.py"))
    assert paths, "helper implementation has not been added yet"
    imported_modules: set[str] = set()

    # Act: inspect imports without relying on runtime module side effects.
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                imported_modules.add(node.module)

    # Assert: none of the legacy private runtime-service imports survive.
    forbidden = sorted(
        module
        for module in imported_modules
        if any(module == private or module.startswith(f"{private}.") for private in PRIVATE_KERNEL_MODULES)
    )
    assert forbidden == []
