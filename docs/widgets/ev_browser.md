# Evidence browser widget documentation
<img src="../../src/cta_orange/widgets/icons/evidence_browser.png" alt="A pixel-art image of a violet eye" width="64px"/>

Let the user see the previous evidence(s) of an `CTA Orange` widget
## Signals
### Inputs
- 1 `CTAData`\
The widget demands 1 `CTA Orange` widget for input. It displays the evidence created by the linked input with or without its payload.
### Outputs
- None
## Description
This is an exploratory widget. Its purpose is to display various evidences created by the software. Linked to a `CTA Orange` widget, it will display the output evidence with or without payload. Previous upstream evidences can be displayed too.
### Interface
![An image of the widget's basic interface](photos/evidence_browser_interface.png)
![An image of the widget's larger interface](photos/evidence_browser_interface_extended.png)
#### Evidence
- **Display payload**: `True` or `False`. Determines if the payload should be displayed.
#### Upstream evidence
- **Display upstream evidence**: `True` or `False`. Determines if the upstream evidences should be displayed.
## Messages
The widget doesn't display messages.
## Example
See the linked example [file](https://github.com/ColinLug/cta_orange/blob/main/examples/example_workflow.ows) for use.
