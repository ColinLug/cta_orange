# Segmentation widget documentation
<img src="../../src/cta_orange/widgets/icons/segmentation.png" alt="A pixel-art image of violet scissors." width="64px"/>

Segment strings.
## Signals
### Inputs
- 1 `CTAData`\
The widget demands 1 `Extract Strings` widget for input.
### Outputs
- `CTAData`\
A group of the ref to the evidence created, here a string store, and the session.
## Description
This widget segments strings extracted from the widget named accordingly into characters or using a typed delimiter.
### Interface
![An image of the widget's basic interface](photos/segmentation_interface.png)
![An image of the widget's extended interface](photos/segmentation_interface_extended.png)
#### Segmentation Options
- **Mode**: `chars` or `delimiter`. If `chars`, segments the strings into characters.
- **Delimiter**: If mode is `delimiter`, the delimiter character or string to use to segment the strings.
- **Send**: Compute and deliver the string store and the table to output.
## Messages
### Errors
- **Upstream data are not connected.**: shown when no input has been linked.
- **The delimiter is empty, please use "chars" mode or provide a legitimate delimiter.**: shown when the delimiter is empty.
## Example
See the linked example [file](https://github.com/ColinLug/cta_orange/blob/main/examples/example_workflow.ows) for use.
