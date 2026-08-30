# CTA Orange

CTA Orange is an add-on for Orange Canvas that provides an interactive authoring
surface for Computational Text Analysis workflows executed by
[CTA Kernel](https://github.com/axanthos/cta_kernel). Version 0.1.0 is the initial
student-developed release prepared for the ComHUM 2026 workflow and currently
provides eight CTA widgets.

The release should be treated as an initial interface implementation: the
conference workflow is supported, while broader interface polish, error handling,
and compatibility hardening remain future work.

The included example workflow compares diversity in emoji strings of different
lengths and evaluates whether the resulting numerical evidence supports a claim.

![A workflow example](cta_orange_workflow_screenshot.png)

## Requirements

- Python 3.12 or later
- Orange3 3.40.0, installed automatically as a package dependency
- CTA Kernel 0.1.0, installed automatically as a package dependency

## Installation

After the 0.1.0 release is published, CTA Orange can be launched in an isolated
`uv` environment with:

```bash
uv run --with cta-orange==0.1.0 python -m Orange.canvas
```

For development from a repository checkout:

```bash
uv sync
uv run python -m Orange.canvas
```

## Example workflow

The repository contains a small synthetic example under [`examples`](examples).
From the repository root, open `examples/example_workflow.ows` in Orange Canvas.
The LoadTSV widget is configured with the relative path
`examples/data/emoji_occurrences.tsv`; if Orange was launched from another
working directory, use the widget's **Browse** button to select that file.

The fixture intentionally gives different source pairs unequal numbers of occurrences.
With the workflow's default comparison threshold (`δ₀ = 0.3`), the source-weighting
sensitivity check therefore distinguishes the pooled endpoint (`δ = 1/12`) from
the equal-source endpoint (`unif_src`, `δ = 7/20`).

## Documentation

Widget documentation is available under [`docs/widgets`](docs/widgets/).

## Development context

The 0.1.0 software release is authored by Colin Lug and Aris Xanthos, in that
order.

CTA Orange was initially developed in the context of a University of Lausanne
student project around CTA Kernel. AI assistants were used during development
and review of parts of the code and documentation. Human contributors reviewed
the resulting material and remain responsible for the released software and
documentation.

Authorship and release metadata for version 0.1.0 are recorded in the published
package and archival release metadata.
