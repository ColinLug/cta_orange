# String Features widget documentation
<img src="../../src/cta_orange/widgets/icons/strings_features.png" alt="A pixel-art image of a violet wide lens." width="64px"/>

Extract and visualize string-level features from a segmented corpus.
## Signals
### Inputs
- 1 `CTAData`\
The widget requires one upstream widget that exports a string view (e.g., `Segmentation`) as input.
### Outputs
- `CTAData`\
A group containing the reference to the newly created evidence (the feature table) and the session.
- `Data Table`\
An Orange data table to visualize the strings.
## Description
This widget extracts string-level features from a segmented corpus. It creates a data table containing strings and their associated features, ordered according to the selected criterion, for visualization and further analysis.
### Interface
![An image of the widget's basic interface](photos/string_features_interface.png)
#### Features
- **Top k**: An integer specifying the number of rows to retain after applying the selected ordering.
- **Order by**: Selects the ordering applied before `Top k`: **Count (descending)** (`count_desc`, default), **Count (ascending)** (`count_asc`), **Length (descending)** (`len_desc`), **Length (ascending)** (`len_asc`), **Variety (descending)** (`variety_desc`), or **Variety (ascending)** (`variety_asc`).
- **Send**: Compute and deliver the feature table to the outputs.
## Messages
### Errors
- **No upstream data connected.**: Shown when no input has been linked.
- **Top k must be a positive integer.**: Shown when the `top k` value is empty, not a number, or less than 1
## Example
See the linked example [file](https://github.com/ColinLug/cta_orange/blob/main/examples/example_workflow.ows) for use.
## Technical notes
- The `order_by` parameter controls the ordering applied before truncation, and the `top_k` parameter controls how many rows are included in the output table.
- The widget validates that `top_k` is a positive integer (≥ 1) before processing.
- The output `Data Table` is an Orange `Table` created from the feature data, with rows and columns mapped directly from the evidence payload.
- The `top_k` field uses a `QIntValidator` to restrict input to positive integers.
