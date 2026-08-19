# Extract strings widget documentation
<img src="../../src/cta_orange/widgets/icons/extract_strings.png" alt="A pixel-art image of a text-file being ruptured" width="64px"/>

Extract strings from a table.
## Signals
### Inputs
- 1 `CTAData`\
The widget demands 1 `LoadTSV` widget for input.
### Outputs
- `CTAData`\
A group of the ref to the evidence created, here a string store, and the session
- `Data Table`\
An Orange data table to visualize the created string store output.
## Description
This widget extracts strings from a given column of a table imported via the `LoadTSV` widget and builds a string store.
### Interface
![An image of the widget's basic interface](photos/extract_strings_interface.png)
#### Importation's mode
- **Column Name**: A valid column name from which the strings will be extracted.
- **ID of sources columns**: Valids column names separated by a comma (`,`) from which extract provenance of the strings.
- **Normalization policy**: `none`, `strip`, `lower`, `nfkc` or `emoji_strip_skin_tone`. Depending on the mode, the strings will be modified (or not) accordingly.
- **Send**: Compute and deliver the string store and the table to output.
## Messages
### Errors
- **Upstream data are not connected.**: shown when no input has been linked.
- **Column(s) not found in upstream table:...**: shown when the columns names couldn't be retrieved from the table.
## Example
See the linked example [file](https://github.com/ColinLug/cta_orange/blob/main/examples/example_workflow.ows) for use.
