# CTA Orange helper migration handoff v0

Status: implementation handoff for the pre-ComHUM consolidation sprint.

## 1. Result

The legacy helper layer has been reimplemented under `cta_orange.helpers` against
released `cta_kernel 0.1.0`. The helper package no longer constructs or exposes
kernel cache, evidence-store, executor, scheduler, resolver, or operator-registry
services.

`CTASession` is retained for this bounded sprint because the current widgets use
one shared session object per authored workspace, pass it with `CTARef` values,
and call session-level evidence and registry conveniences throughout the canvas.
Removing that façade would therefore require broad transport and lifecycle edits.
The retained class is intentionally thin: it owns one public `KernelRuntime`, one
Orange-owned `GraphRegistry`, workspace identity/scope, and retained public
`RunResult` objects needed to form later output references.

## 2. Retained helper symbols

The following legacy concepts remain, with new imports under `cta_orange.helpers`:

- `CTARef`: retained with the same transport fields and `from_evidence` factory.
- `GraphRegistry` / `NodeRecord`: retained as Orange-owned mutable authored-graph
  state. Compilation emits schema `0.1` `GraphSpec` objects and does not perform
  kernel scheduling or admissibility.
- `CTASession`: retained as the thin façade described above. `ensure_computed`
  now returns public `RunResult` rather than the legacy private `RunLog`; current
  widgets ignore that return value.
- `KernelWidgetLogic`: retained for common widget commit/delete mechanics.
- `OWCTAKernelBase`: retained as the Orange-specific base class and kept
  headless-importable for helper testing.

The legacy `orangecta.cta_kernel.helpers` namespace is removed rather than
recreated as a compatibility façade.

## 3. Mechanical widget adaptations

Every current helper import should move from `orangecta.cta_kernel.helpers...`
to the corresponding `cta_orange.helpers...` module. No signal-shape change is
required by this helper migration: the existing `(CTASession, CTARef)` transport
can remain during Colin's bounded widget pass.

The paths below describe the current repository layout only. They are not a
packaging recommendation. During Colin's package-consolidation work, the widgets
should ultimately move under the `cta_orange` package (for example
`src/cta_orange/widgets/...`) so that helpers and widgets belong to the same
distribution namespace. That relocation is outside this bounded helper slice.

The affected widget modules in the current tree are:

- `src/widgets/load.py`
- `src/widgets/extract_string.py`
- `src/widgets/segmentation.py`
- `src/widgets/filter_strings.py`
- `src/widgets/string_features.py`
- `src/widgets/proportion.py`
- `src/widgets/claim.py`
- `src/widgets/ev_browser.py`

For Load, ExtractStrings, Segmentation, FilterStrings, StringFeatures, and
Proportion, the retained `CTASession.evidence`, registry, output-ref, and common
base APIs are sufficient apart from the separate corrections below.

## 4. Required widget-contract corrections

These are Colin's widget-level responsibilities and are not implemented in the
helper migration.

### FilterStrings and Proportion

Both import the legacy private predicate parser. Do not reproduce that parser in
the helper layer. Their eager UI validation should be removed or redesigned so
released kernel admissibility/execution remains authoritative.

### Claim

Claim directly scans `session.store`; the thin session deliberately has no
`store`. Replace that behavior with public evidence-history access through
`session.all_evidence()` / `session.evidence(...)` as appropriate. Its direct
registry calls remain available, but the widget still needs the previously
identified released-kernel contract fixes: lowercase `threshold` / `compare`
parameter values and support for absent optional B input so the kernel can
materialize `UNDER_SUPPORTED`.

Claim's multi-input handling must also reject or otherwise resolve inputs from
different workspaces before authoring edges. `GraphRegistry.set_input` now
rejects cross-workspace references explicitly.

### EvidenceBrowser

EvidenceBrowser also accesses `session.store` directly. Replace lookup and
history enumeration with `session.evidence(ref)` and `session.all_evidence()`.
No raw evidence-store compatibility property should be added to `CTASession`.

## 5. Helper behavior changes relevant to widget review

Target execution now compiles only the selected target's present authored
upstream closure and delegates formal checking, scheduling, caching, execution,
and evidence retention to `KernelRuntime`. An unrelated under-supported branch
therefore does not block an independently valid target.

Deleting a widget prunes authored registry edges but deliberately does not erase
runtime evidence history. Unknown evidence is reported through the kernel's
public `OutputResolutionError`; a cross-workspace `CTARef` is rejected first at
the Orange boundary with `ValueError`.

## 6. Dependency and validation note

`pyproject.toml` now declares `cta-kernel==0.1.0`. The helper contract passes
against the researcher-supplied released-kernel snapshot, and the repository-level
test run is green apart from the deliberate self-expiring widget smoke-test skip
described below.

The working repository does contain `uv.lock`; RF snapshots intentionally do not
ship it. The researcher supplied the current lockfile separately while closing
this slice, so absence of `uv.lock` from snapshots is not a migration blocker and
does not imply that the repository lock needs to be created.

The pre-existing `tests/test_load.py` imports `widgets.load`, whose helper
imports remain in the intentionally removed legacy `orangecta.cta_kernel.helpers`
namespace until Colin performs the widget-maintainer migration. The smoke test is
therefore explicitly skipped while that exact legacy namespace is still present
in `src/widgets/load.py`; its existing assertion is unchanged, and collection
automatically resumes once the widget imports are migrated. This keeps repository-
level `pytest` usable without recreating a forbidden compatibility façade or
claiming that widget migration belongs to the helper slice.

## 7. Temporary ResearchFlow project status

For the duration of this bounded helper slice, the current `cta_orange` checkout
is intentionally being used as a ResearchFlow project so the researcher can use
the RF snapshot/patch workflow while working in Colin's repository.

The temporary RF project slug is `cta-orange`. The hyphenated slug is deliberate:
RF patch filenames delimit their project token with underscores, so the earlier
temporary slug `cta_orange` made patch association ambiguous. Patches targeting
this checkout must therefore use `rf_patch_cta-orange_...zip` and manifests must
declare `project = "cta-orange"`. This RF-only slug does not rename Colin's
repository, the Python distribution, or any import package.

This is a temporary operational exception, not a decision that Colin's repository
should permanently contain the ResearchFlow record. The temporary `ai/` and
`.researchflow/` material is accepted only for the bounded helper slice.

At slice close, cleanup is an explicit handoff obligation. Before the repository
is returned to Colin's normal stewardship, review and remove the temporary RF/AI
material from his workspace and determine the appropriate history cleanup so
temporary research-process records are not inadvertently retained. Preserve any
durable project-level record still needed in the governing LingMod/RF context
before that cleanup.

## 8. Bounded helper slice completion

The helper migration is complete for this bounded pre-ComHUM slice. The delivered
helper layer is `cta_orange.helpers`, backed by the public `cta_kernel 0.1.0`
runtime rather than duplicated private kernel services. The helper contract tests
and repository-level tests pass under the boundary described above.

No further helper-side implementation is required before handoff to Colin. The
remaining work is widget/package work under Colin's responsibility:

- migrate current widget imports to `cta_orange.helpers`;
- adapt Claim and EvidenceBrowser away from raw evidence-store access;
- remove or redesign legacy eager predicate parsing so kernel validation remains
  authoritative;
- apply the other widget-contract corrections recorded in this handoff;
- relocate the widget package from the current top-level `src/widgets` layout
  under `cta_orange` as part of package consolidation.

The current RF enablement of Colin's checkout has now served its bounded purpose.
Before handing the repository back, preserve this durable handoff in the governing
LingMod/RF record, then remove the temporary `ai/` and `.researchflow/` material
from Colin's workspace and repair repository history as appropriate so those
temporary research-process records are not inadvertently retained. The cleanup
must not remove the actual helper implementation, tests, dependency changes, or
this handoff content until its durable copy has been preserved elsewhere.
