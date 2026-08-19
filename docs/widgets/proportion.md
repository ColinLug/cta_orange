# Extract strings widget documentation
<img src="../../src/cta_orange/widgets/icons/proportion.png" alt="A pixel-art image of a left tilted scale." width="64px"/>

Compute a proportion of strings following a certain predicate.
## Signals
### Inputs
- 1 `CTAData`\
The widget requires a widget exporting a string view for input.
### Outputs
- `CTAData`\
A group of the ref to the evidence created, here a scalar, and the session
## Description
This widget computes a proportion of strings following a certain predicate. It's meant to allow a certain claim to be made given scalars.
### Interface
![An image of the widget's basic interface](photos/proportion_interface.png)
#### Propotion
- **Compute proportion where**:  A valid predicate to compute the proportion of certain type of strings. Valid predicates includes : `len`, `variety` or `count` variables.
- **Send**: Compute and deliver the scalar to output.
## Messages
### Informations
- **No predicate configured yet**: shown when the predicate is empty.
### Errors
- **Upstream data are not connected.**: shown when no input has been linked.
- **Invalid predicate:...**: shown doesn't follow the standard grammar.
## Example
See the linked example [file](https://github.com/ColinLug/cta_orange/blob/main/examples/example_workflow.ows) for use.
