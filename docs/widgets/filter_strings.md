# Filter Strings widget documentation
<img src="../../src/cta_orange/widgets/icons/filterstrings.png" alt="A pixel-art image of a violet funnel" width="64px"/>

Filter strings using a given predicate.
## Signals
### Inputs
- 1 `CTAData`\
The widget requires one upstream `Segmentation` widget as input. It expects a string store or string view containing the strings to filter.
### Outputs
- `CTAData`\
A group of the ref to the evidence created, here a filtered string store, and the session
## Description
This widget is intended to filter out strings that do not satisfy a specified predicate. It helps select specific strings from the data for further analysis or comparison.
### Interface
![An image of the widget's basic interface](photos/filter_strings_interface.png)
#### Filter Options
- **Including strings where**: A valid predicate to keep only strings matching certain criteria. Valid predicates should use variables like `len`, `variety`, or `count`.
- **Send**: Compute and deliver the filtered string view  to output.
## Messages
### Informations
- **No predicate configured yet**: Shown when the predicate field is empty.
### Errors
- **Upstream data are not connected.**: Shown when no input has been linked.
## Example
See the linked example [file](https://github.com/ColinLug/cta_orange/blob/main/examples/example_workflow.ows) for use.
## Technical notes
- The predicate is written in a custom DSL (Domain-Specific Language) and is parsed using `parse_predicate()` from the `cta_kernel.operators.predicate_dsl` module.
