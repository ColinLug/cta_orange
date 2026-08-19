# Load widget documentation
<img src="../../src/cta_orange/widgets/icons/load.png" alt="A pixel-art image text-file being imported" width="64px"/>

Import a `.TSV` file and create a session.
## Signals
### Inputs
- None
### Outputs
- `CTAData`\
A group of the ref to the evidence created, here a table, and the session
- `Data Table`\
An Orange data table to visualize the imported `.TSV`.
## Description
This widget is intended to be the first one of a worflow. It helps import the data needed for an analyze.
### Interface
![An image of the widget's basic interface](photos/load_interface.png)
#### Source
- **File path**: A valid path to a `.TSV` file to import.
#### Scope labels
- **Dataset**: A name for the imported dataset.
- **Slice ID**: An ID for the slice of the dataset. Currently `all_strings` only.
- **Send**: Compute and deliver the table to output.
## Messages
### Informations
- **Dataset ID is empty. Don't forget to annotate it.**: shown when the name of the dataset is empty.
### Errors
- **Please provide a valid path.**: shown when the file couldn't be retrieved from the path.
- **Please provide a TSV file.**: shown when the file isn't a `.TSV` file.
## Example
See the linked example [file](https://github.com/ColinLug/cta_orange/blob/main/examples/example_workflow.ows) for use.
