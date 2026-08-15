# Claim widget documentation
<img src="../../src/cta_orange/widgets/icons/claim.png" alt="A pixel-art image of a violet beaker brewing" width="64px"/>

Determine whether a scientific claim is supported by the corpus evidence.
## Signals
### Inputs
- 1 or 2 `CTAData`\
The widget demands 1 or 2 `Proportion` widget(s) for input, depending on the mode set. If the mode is "Compare", then 2 `Proportion` widgets must be linked as input. Otherwise, if the mode is "Threshold", then only 1 is needed.
### Outputs
- `CTAData`\
A group of the ref to the evidence created, here a claim, and the session
- `Data Table`\
Only if running sensitivity check
## Description
This is the final widget of the workflow. Its purpose is to determine whether a claim can be scientifically validated by the data and its sources.
### Interface
#### Options
- **Mode**: `Compare` or `Threshold`. Determines which of the two parameters below is used and how many upstream Proportion widgets are required.
- **θ (theta)**: threshold value used in `Threshold` mode. The scalar input must exceed this value.
- **δ₀ (delta)**: minimum margin required between the two scalar inputs in `Compare` mode.
- **Run source-weighting policy check**: launches a robustness sweep across source-weighting policies; results are shown as a Data Table output (see "Sensitivity check" below).
- **Send**: Compute and deliver the claim in `Computed Result`
#### Computed Result
- **Status**: verdict of the claim check (e.g. `Supported`, `Not supported`, `Undetermined`), from the evidence payload.
- **Reason**: the reason behind the status, as reported by the kernel.
- **Missing inputs**: the list of inputs missing when the claim was evaluated.
- **Mismatches**: any compatibility mismatch detected between the two scalar inputs (e.g. incompatible scope or normalization policy).
#### Sensitivity check
The "Run source-weighting policy check" button launches a separate
robustness sweep, independent from the main Send button. It checks
how the claim's outcome would change under a grid of source-weighting
policies, and displays the result as a table on the Data Table output.
## Messages
### Errors
- **Upstream data(s) are not connected.**: shown when one or both scalars are missing.
- **Sweep failed**: shown when the robustness sweep raises an exception.
## Example
See the linked example [file](https://github.com/ColinLug/cta_orange/blob/main/examples/example_workflow.ows) for use.
