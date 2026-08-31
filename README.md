# CTA Orange
`CTA Orange` is an add-on for Orange Canvas created for Computational Text Analysis and based on [CTA Kernel](https://github.com/axanthos/cta_kernel). It adds 8 new widgets meant to propose an interface based edit of a CTA Kernel's workflow. It is designed to illustrate the possibility of making scientific claims about text analysis in an interactive and visual way. The bundled [example](https://github.com/ColinLug/cta_orange/tree/main/examples) uses synthetic data to illustrate a workflow comparing the diversity of emoji strings of different lengths and evaluating whether the resulting evidence supports a claim.

![A workflow example](cta_orange_workflow_screenshot.png)
## Requirements
- Python ≥ 3.12
- Orange3 3.40.0
- [CTA Kernel](https://github.com/axanthos/cta_kernel) 0.1.0

For development from source, [uv](https://docs.astral.sh/uv/) is also required.

## Installation
For regular use, install the released package from PyPI:
```bash
python -m pip install cta-orange==0.1.0
```

For development from a repository checkout, open a terminal in the folder containing `pyproject.toml` and run:
```bash
uv sync
```
## Running
After a regular installation, launch Orange with:
```bash
python -m Orange.canvas
```

From a development checkout managed with `uv`, use:
```bash
uv run python -m Orange.canvas
```
## Documentation
Each widget has its own documentation under [`docs/widgets`](docs/widgets/).

## Development context
These widgets have been created by Colin Luginbühl in the context of a UNIL course under the supervision of Aris Xanthos who designed the `CTA Kernel` infrastructure.\
AI assistants, including Claude, Deepseek, and ChatGPT models, have been used for reviewing parts of the code and documentation. Nevertheless, the authors declare full responsibility for the created widgets and documentation.
