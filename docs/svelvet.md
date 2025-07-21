Svelvet

Build and interact with node-based user interfaces using Svelte
​
Description
Svelvet is a lightweight and infinitely customizable component library used to build interactive, node-based user interfaces. The stars of Svelvet are its Nodes, Anchors and Edges. A node is a rectangular block. An edge is the line or string 🧶 used to connect nodes. An anchor is a small circle ⚫ that one or many edges are able to connect. Canvases are composed structurally by passing Groups, Nodes and other components as children to the Svelvet wrapper. Standard Svelte syntax applies for conditional rendering and iteration to place Nodes on the canvas. Default Nodes can be configured by passing props to the Node component, but wrapping custom components or HTML elements in a Node component allows for greater flexibility and functionality. Edges, the connections between Anchors, can be specified ahead of time or dynamically and are fully customizable. Default canvas styling can be configured via specific props or, more generally, by specifying a theme such as light or dark. You can also place arbitrary HTML elements on the canvas, which is especially useful for notes and annotations.


Svelvet

Primary canvas component configurable via props. Enables zoom, pan and translation of the canvas.
​
Description
Svelvet is the wrapping parent component that renders out nodes and edges. It is configurable via props, but no props are required. Many props can be set globally at this level and then overriden at the Node, Edge or Anchor level.
App.svelte
Copy

<script>
  import { Node, Svelvet, Minimap, Controls } from 'svelvet';
</script>

<Svelvet id="my-canvas" width="{500}" height="{500}" TD minimap controls locked>
  <Node />
  <Node id="alpha" bgColor="red" label="Default Node" />
</Svelvet>

​
Props
​
width
number
default:"size of wrapping element"
Width of the canvas window on the DOM. If not passed, element will fill its wrapping container.
​
height
number
default:"size of wrapping element"
Height of the canvas window on the DOM. If not passed, element will fill its wrapping container.
​
id
number | string
default:"incrementing integer"
Identification for the canvas. If not passed, defaults to an incrementing integer. Used as the HTML id value for the element taking the form G-id.
​
minimap
boolean
default:"false"
Boolean used to render the default Minimap component. Just pass “minimap” rather than minimap= .
​
translation
{x: number, y: number}
default:"{x: 0, y: 0}"
Initial translation of the graph. Does not currently feature two-way data binding.
​
controls
boolean
default:"false"
Boolean used to render the default Controls component. Just pass “controls” rather than controls= .
​
edge
Edge Component
A custom Edge component to be used as the global Edge style for the canvas. Can be overridden at the Node and Anchor level.
​
edgeStyle
bezier | step | straight
default:"bezier"
Enum representing the global edge style for the canvas. Overriden when passing custom Edges.
​
endStyles
['arrow' | null , 'arrow' | null]
default:"[null , null]"
Enum representing the global end styles for the canvas. First element in array will be applied to the start of the edge, second element in array will be applied to the end of the edge. Overriden when passing custom Edges.
​
snapTo
number
default:"1"
Pixel value at default scale that Nodes should snap to when being moved.
​
fixedZoom
boolean
default:"false"
Prevents zooming on the canvas.
​
pannable
boolean
default:"false"
Prevents panning on the canvas.
​
editable
boolean
default:"true"
Allows the Node properties to be edited via CTRL+click.
​
fitView
boolean
default:"false"
Adjusts scale and translation to fit all Nodes in view on mount.
​
locked
boolean
default:"false"
Locks node movement, but still allows the canvas to be panned.
​
initialZoom
number
default:"1"
Sets the initial zoom level for the canvas. Below 1 zooms out, above 1 zooms in.
​
theme
string
default:"light"
A string associated with a custom theme created using a :root[svelvet-theme="theme-name"] CSS selector. Svelvet reserves light and dark.
​
mermaid
string
default:""
canvas representation using Mermaid-inspired string syntax. Great for quickly developing simple Nodes and Edges.
​
mermaidConfig
string
An object of key value pairs where the key is a Node ID and the value a Node configuration object. Used only when creating canvases via the Mermaid syntax.
​
TD
boolean
default:"false"
Boolean controlling the directionality of the canvas. TD being set false by default means that the canvas direction is inherently left-to-right. Pass “TD” as a prop to change the direction to top-down.
​
disableSelection
boolean
default:"false"
Boolean controlling whether or not Shift + Click enables the selection of multiple components. This feature is enabled by default.
​
edgesAboveNode
boolean | 'all'
default:"false"
Sets whether Edges should, by default, be placed above or below connected Nodes. Can be set to all to force Edges above all nodes. Otherwise, true essentially turns on raiseEdgesOnSelect, but places the edges at higher z-Index than the Node.
​
raiseEdgesOnSelect
boolean | 'source' | 'target'
default:"false"
When a Node is selected, this prop controls whether the z-index of a connected edge should be raised. Setting to true raises the edge regardless of if the source or target is selected.
​
modifier
'alt' | 'ctrl' | 'meta' | 'shift'
default:"meta"
Sets global key modifier used to detect select all and duplicate events.
​
trackpadPan
boolean
default:"false"
When using a trackpadPan, setting this prop to true enables two finger pan on the Graph and pinch to zoom. Will conflict with scroll behavior on mice. This mode of navigation can be enabled dynamically by hodling down the meta key.
​
Events
​
on:edgeDrop
Fires when an Edge connection is started and not completed. Does not fire on drops after a disconnection.
​
on:connection
Fires whenever a new Edge is created.
​
on:disconnection
Fires whenever an Edge is removed.



Components
Node

Primary canvas element. Configurable via props or by passing a custom node as children
The props interface for the Node component is available by importing the NodeConfig type
​
Description
A Node can be configured in two primary ways. First, you can customize the default node by passing props to control color, border, size, position, etc. Second, you can wrap your own custom components with our Node component and use the exposed actions, properties and events however you choose. Pass the entire component as a child of the Svelvet component to render it on the canvas.
+page.svelte
Copy

<script>
  import { Node, Svelvet } from 'svelvet';
  import MyNode from './MyNode.svelte';
</script>

<Svelvet>
	<MyNode />
	<Node id="alpha" bgColor="red" label="Default Node" />
</Svelvet>

When creating custom nodes, styling should be handled entirely within the context of your component. Passing props to the Node wrapper may not result in your intended styling. If you’d like the Node to be resizable, you can set initial dimensions via props, but set your CSS width and height to 100%
​
Props
​
position
{x: number, y: number}
default:"{x: 0, y: 0}"
The position of the Node. These correspond to pixel values at the default graph scale. This prop newly features two way data binding. Please report any issues on GitHub.
​
dimensions
{ width: number, height: number }
default:"{ width: 200, height: 100 }"
Initial dimensions of the node. Pixel value based on initial scale.
​
connections
Array<[nodeId, anchorId] | nodeId>
default:"[]"
Used to specify Node connections ahead of time. Array of tuples representing a node/anchor pair or of nodeIds themselves. IDs can be strings or numbers. When specifying nodeIds only, connections are spread evenly across the input anchors of the target.
​
id
number | string
default:"incrementing integer"
Identification for the node. If not passed, defaults to an incrementing integer. Used as the HTML id value for the element taking the form N-id.
​
edge
Edge Component
A custom Edge component to be used as the default Edge style for the Node. Can be overriden at the Anchor level.
​
inputs
number
default:"1"
Number of input anchors placed on the node.
​
outputs
number
default:"1"
Number of output anchors placed on the node.
​
drop
'cursor' | 'center'
default:"false"
When passed a value, the initial drop position of the Node is set to the current relative cursor position or the current viewport center.
​
useDefaults
boolean
default:"false"
When creating custom Nodes, pass the useDefaults prop to use Svelvet’s default Node styling.
​
bgColor
CSS Color String
default:"theme dependent"
The initial background color of the node. Default changes based on theme.
​
borderColor
CSS Color String
default:"theme dependent"
The initial border color of the node. Default changes based on theme.
​
rotation
number
default:"0"
Initial roation of node. Can be set dynamically when the Node is resizable.
​
borderWidth
number
default:"1"
Pixel value of the border at default scale.
​
textColor
CSS Color String
default:"theme dependent"
The initial text color of the node. Default changes based on theme.
​
selectionColor
CSS Color String
default:"theme dependent"
Color of the border when the node is selected.
​
label
string
default:""
Label for the default node. Centered horizontally and vertically
​
TD
boolean
default:"false"
Controls the default direction of the canvas. When true, input anchors on top and output anchors on the bottom. If neither TD or LR are passed, node direction defaults to canvas direction.
​
LR
boolean
default:"false"
Controls the default direction of the canvas. When true, input anchors are placed on left and output anchors on the right. If neither TD or LR are passed, node direction defaults to canvas direction.
​
zIndex
number | Infinity | -Infinity
default:"1"
Initial stacking placement of the node. To force a node to the top or bottom at all times, pass Infinity or -Infinity.
​
editable
boolean
default:"true"
Determines whether the node properties can be edited via right click. Populates Editor which gives user the ability to delete selected node, edit label name and edit height and width via resize button. Resize input does not need unit, just the number - for example: 200.
​
locked
boolean
default:"false"
Prevents node from being moved. Can be set at the canvas level.
​
center
boolean
default:"false"
When true, the Node is mounted in the optical center of the viewport
​
dynamic
boolean
default:"false"
Enables dynamic Anchor positioning based on relative position of connected Nodes
​
Actions
​
let:grabHandle
Accessed via the let directive. Placed on an element (use:grabHandle) you would like to control movement and selection of the Node.
​
Events
​
on:nodeClicked
Fires when the node is clicked.
​
on:nodeReleased
Fires when when a mouse up event occurs on the Node. Does not fire if the Node has been dragged and then released.
​
on:duplicate
Fires whenever a Node is selected and the user triggers a modifier key command with the ‘D’ key pressed.
​
Properties
​
let:selected
boolean
Boolean representing whether or not the node is currently selected. Toggle classes by passing to an element using the class directive (class:selected).
​
let:node
object
The Node object from the Svelvet internal store.
​
Functions
​
let:connect
Use to programatically create connections from Nodes. Accepts a single Node ID or a [Node ID, Anchor ID] tuple.
​
let:disconnect
Use to programatically remove connections from Nodes. Accepts a single Node ID or a [Node ID, Anchor ID] tuple.
Svelvet
Anchor
twitter
github
linkedin
Powered by Mintlify



This component is only used when constructing custom Nodes
​
Description
Anchors are the ports or small circles ⚫ on a node that allow for the connection of edges(the connection strings). Anchors are passed as children to a Node component and can be placed anywhere using CSS. The visual representation of an Anchor can be customized by passing an HTML element or Svelte component as a child. Properties representing the state of the Anchor are exposed via the let directive. The booleans can control CSS styling of custom anchors using the class directive. When using Svelvet as a data flow system, Anchors also accept input and output stores as props. Connections made between Anchors will also connect the stores. Anchors can be created as inputs, outputs or default. This specification controls connection logic and directionality of the corresponding Edges. Finally, Edge connections can be specified at runtime by passing an array of tuples via the connections prop. Each tuple represents a corresponding user-defined Node and Anchor ID.
MyNode.svelte
Copy

<script lang="ts">
    import { Node, Anchor } from 'svelvet';
    import type { Connections } from 'svelvet';
    import CustomAnchor from './CustomAnchor' // A Svelte component or HTML element of your creation
    const connections: Connections = [["node1", "4"],["node2", "3"]]
  </script>

  <Node let:selected>
    <div class:selected>
      <div class="input-anchors">
        <Anchor bgColor="red" id="data-connection" input />
        <Anchor multiple input nodeConnect/>
      </div>
      <div class="output-anchors">
        <Anchor let:linked let:hovering let:connecting output >
          <CustomAnchor {linked} {hovering} {connecting} />
        </Anchor>
        <Anchor direction="east" {connections}  output />
      </div>
    </div>
 </Node>

​
Props
​
id
string | number
default:"incrementing integer"
Identification for the Anchor. If not passed, defaults to an incrementing integer starting at 1 for each Node. Used as the HTML id value for the element taking the form A-id/N-id
​
invisible
boolean
default:"false"
Prevents the default Anchor from rendering. When passing custom Anchors as children, it is not necessary to set this prop to true. Usually used in combination with the nodeConnect prop.
​
nodeConnect
boolean
default:"false"
Boolean that determines whether mouse up events on the parent Node should trigger connections to the Anchor. When this value is true for multiple Anchors, connections will be made to open Anchors in order.
​
input
boolean
default:"false"
Boolean that specifies the anchor can only connect to output or no-preference anchors. When not passed, anchor allows all connections.
​
output
boolean
default:"false"
Boolean that specifies the anchor can only connect to inputs or no-preference anchors. When not passed, anchor allows all connections.
​
multiple
boolean
default:"input/output dependent"
Boolean used to control whether input anchors can have multiple connections. This is false for input anchors and true for output and no-preference anchors.
​
direction
north | south | east | west
default:"canvas direction dependent"
Enum used to control the “directionality” of the anchor. By default, an input anchor on the left side of the node has a directionality of “west”. This is used to control the curvature of the edge.
​
dynamic
boolean
default:"false"
Enables dynamic Anchor positioning based on relative position of connected Nodes
​
edge
Svelte Component | null
default:"null"
An Edge component associated with the Anchor. Every connection made from this Anchor will render out the corresponding Edge.
​
edgeLabel
string
default:""
When not passing a custom Edge component, this prop can be used to set the label for all Edges initiated from the Anchor
​
edgeColor
Writable<CSS Color String>
default:"theme dependent"
This prop accepts a store value associated with a CSS Color String. It applies to both default and custom Edges so long as the latter do not render out a custom path or pass a color prop.
​
connections
Array<[nodeId, anchorId] | nodeId>
default:"[]"
Used to specify Node connections ahead of time. Array of tuples representing a node/anchor pair or of nodeIds themselves. IDs can be strings or numbers. When specifying nodeIds only, connections are spread evenly across the input anchors of the target.
​
locked
boolean
default:"false"
Prevents Anchor from being connected/disconnected
​
inputsStore
ReturnType<typeof generateInputs> | null
default:"null"
When using our data flow system, this is the store of possible inputs for the Node and is the return value of the function generateInputs.
​
outputStore
Readable<unknown> | null
default:" null"
When using our data flow system, this is the store associated with a data output of a node. It is return value of the function generateOutput.
​
key
string | null
default:"null"
Key associated with the input store.
​
bgColor
CSS Color String
default:"theme dependent"
Used for styling the default anchor
​
Properties
​
let:linked
boolean
True when the Anchor has an active connection.
​
let:connecting
boolean
True when the Anchor is rendering a temporary Edge connected to the cursor.
​
let:hovering
boolean
True when the cursor is over the Anchor element.
Node
Edge
twitter
github
linkedin


Edge

Optional component for customizing Edges and Edge labels
​
Description
Edges are the strings 🧶 used to connect nodes. Visualization and interaction behavior can be customized for Edges by creating your own custom components. Edges styling can be fully controlled via CSS by passing the expose “path” variable on an HTML Path Element. Custom labels can also be passed via the “label” slot. Custom Edges are then passed as children to the Anchor component or via the “edge” prop of an Anchor component. Any Edge initiated from that Anchor will render out your custom path and label. Edges can also be passed to the Svelvet and Node components, enabling the ability to set a global Edge style which can be overriden at the Anchor or Node level. Edges also accept callback functions that run in response to click events on the path.
When customizing the Edge path via your own path element, props controlling the Edge apperance such as color, width and animate will no longer apply
Copy

<script>
	import { Edge } from 'svelvet';
</script>

<Edge let:path let:destroy edgeClick="{() => alert('Edge clicked')}" step>
	<path d={path} />
	<button on:click={destroy} slot="label">
		<p>Custom Label</p>
	</button>
</Edge>

<style>
	path {
		stroke: rgb(246, 231, 20);
		stroke-width: 4px;
	}
</style>

​
When passing a custom label, you must specify slot=“label”
​
Props
​
width
number
default:"2"
Pixel width of stroke at scale 1.
​
edgeClick
(() => void) | null
default:"null"
Function to run when a click event is fired on an Edge.
​
targetColor
CSSColorString
Color of the Edge click target. Set to opacity 50%. Only displayed when an edgeClick function is passed.
​
color
CSS Color String
default:"theme dependent"
Color of the edge path.
​
straight
boolean
default:"false"
Boolean controlling curvate of edge path. Renders edge as straight line.
​
step
boolean
default:"false"
Boolean controlling curvate of edge path. Renders edge using “step” logic.
​
cornerRadius
number
default:"8"
Radius of corners when rendering out a step path. Set to 0 for hard corners.
​
animate
boolean
default:"false"
Renders edge path as a dashed, moving line.
​
start
'arrow' | null
default:"null"
Adds an arrow to the start of the edge path.
​
end
'arrow' | null
default:"null"
Adds an arrow to the end of the edge path.
​
label
string
Label text.
​
labelColor
CSS Color String
default:"theme dependent"
Color of the label.
​
textColor
CSS Color String
default:"theme dependent"
Color of the label text.
​
enableHover
boolean
default:"false"
Allows edges to be highlighted when hovering over them.
​
labelPosition
number
default:"0.5"
Places the label at a certain position along the Edge path. Defaults to middle. Value must be between 0 and 1.
​
Properties
​
let:path
string
The SVG path string used for rendering the edge. Pass to the “d” parameter on your custom path component.
​
let:hovering
boolean
True when the cursor is over the Edge element.
Note: You must set enableHover to true for this value to work.
​
Functions
​
let:destroy
function
Function to remove the edge and break Anchor connections.


Components
Drawer

Optional component offering drag and drop functionality of Default Nodes and Custom Nodes which are configurable via props
​
Description
The Drawer is a self-wrapping parent component which renders out a Svelvet component and a Drawer Controller on the canvas. The drawer controller provides an interactive UI with drag and drop functionality for creating and customizing Svelvet components before adding them to the canvas. The styling of Nodes, Edges and Anchors are fully configurable by selecting the props that are available to these components to change their visualization and interaction behavior. All the props that are available to the Svelvet component are available to be passed on to the Drawer component. See Svelvet For the list of available props to be passed on to the Drawer component.
When customizing props for Anchors and Edges, the props such as Label, Default Anchors & Anchor position for creating a Node will no longer apply.
MyDrawer.svelte
Copy

<script>
    import {Drawer, ThemeToggle} from 'svelvet';
</script>

<Drawer height={1200} zoom={0.70} controls>
   <ThemeToggle main='light' alt='dark' slot='toggle'/>
</Drawer>

​
Notes
Adding an anchor will create a custom node and override all default node settings. The anchor direction prop functions differently from a typical anchor component by modifying both its position and the rendered edge directions. Check out the video demo of the drawer functionality. 

Group

A Group of Nodes represented by a bounding box
​
Description
A Group component can be used to wrap a set of a Nodes and limit their movement to within the bounds of the Group. These can be created dynamically using Shift + Meta + Click, but can be specified ahead of time using the Group component.
App.svelte
Copy

<script>
  import { Svelvet, Group, Node } from 'svelvet';
</script>

<Svelvet>
    <Group color="lightblue" groupName="my-group" position={{x: 300, y: 400}} width={600} height={200}>
        <Node/>
        <Node/>
    </Group>
</Svelvet>

​
Props
​
groupName
string | number
required
Identification for the Group.
​
width
number
required
Width of the bounding box relative to a scale of 1.
​
height
number
required
Height of the bounding box relative to a scale of 1.
​
position
{x: number, y: number}
default:"{x: 0, y: 0}"
The position of the Group.
​
color
CSS Color String
default:"random color"
The color of the group box.

Description
The Resizer component can be passed to a custom Node to enable dynamic resizing and rotation. Dimensions allowed for resizing and minimum dimensions can be set via props.
MyNode.svelte
Copy

<script>
	import { Node, Resizer } from 'svelvet'
</script>

<Node let:selected dimensions={{ width: 400, height: 100 }}>
	<div class="node" class:selected>
    	<Resizer width height rotation/>
    </div>
</Node>

<style>
	.node {
		width: 100%;
		height: 100%;
		background-color: red;
		border-radius: 8px;
		border: 2px solid black;
	}
	.selected {
		border: 2px solid white;
	}
</style>

When using the Resizier component. You must specify your root level HTML element width and height as 100%. Set initial size via Node props.
​
Props
​
width
number
default:"false"
Boolean controlling whether the Node can be resized along its width.
​
height
number
default:"false"
Boolean controlling whether the Node can be resized along its height.
​
rotation
boolean
default:"false"
Boolean controlling whether the Node can be rotated via the top left corner.
​
minWidth
number
default:"200"
Pixel value reprsenting the minimum alowed height when resizing.
​
minHeight
number
default:"100"
Pixel value representing the minimum allowed width when resizing.

Minimap

Plugin component that displays a map of all nodes on the canvas
​
Getting started
The Minimap component can be rendered by either passing the shorthand prop minimap to the Svelvet component or by passing the entire Minimap component as a child, allowing further configuration via props. Nodes can be hidden/unhidden on the Minimap if you pass the hideable prop.
When passing the component to Svelvet, you must specify slot=“minimap”
App.svelte
Copy

<script>
  import { Svelvet } from 'svelvet';
</script>

<Svelvet>
  <Minimap width="{100}" corner="NE" mapColor="blue" slot="minimap" />
</Svelvet>

​
Props
​
corner
enum
default:"SE"
Controls corner placement of the Minimap component.
​
width
number
default:"100"
Width dimension of the Minimap component.
​
height
number
default:"0"
Height dimension of the Minimap component. If not passed, Minimap will render out as a square with both dimensions equal to the width value.
​
hideable
boolean
default:"false"
Boolean controlling whether Nodes can be hidden by clicking on their Minimap representation.
​
mapColor
CSS Color String
default:"theme dependent"
Background color of minimap.
​
nodeColor
CSS Color String
default:"Node Color"
Color of the minimap node elements. Defaults to actual node color.
​
borderColor
CSS Color String
default:"theme dependent"
Border color of the Minimap wrapper.


Overview
​
Concepts
Connections between Anchors can be made functional by passing input and output stores via props. An input store is a Svelte writable with string keys and writable numbers, strings, objects, arrays or booleans as the values. In general terms, the return type of generateInput is a Writable<Record<string, Writable<unknown>>>, though, this is a simplification for illustrative purposes. An output store is a custom readable derived from the current values of each parameter in an input store. Every time a parameter changes, the output store is rederived according to a user provided processors function. A processor function is a user-defined callback that is called with the current values of the input store. An output store returns a single value. To facilitate easier setup, we have created a series of functional components that can control Node parameters as well has some helper functions to format parameters for use in this model and generate outputs based on a provided processor function. Below is an example Node that has three parameters: two integer values controlled via Sliders and an “option” value, controlled via a RadioGroup, representing the mathematical operation to apply to the integer values. When connections are made to input Anchors, the writable associated with the corresponding key is overwritten with the readable store associate with the output anchor that connected to it. Upon disconnection, a new writable is created with the last value of the output prior to disconnection.
Copy

<script lang="ts">
    import { Node, Anchor, Slider, RadioGroup } from 'svelvet'
    import { generateInput, generateOutput } from 'svelvet'

    // Type your input structure
    type InputStructure = {
        value1: number;
        value2: number;
        option: string;
    };

    // Create initial values for your parameters
    const initialData = {
        value1: 10,
        value2: 30,
        option: 'multiply'
    };

    // Generate a formatted inputs store
    const inputs = generateInput(initialData);

    // Specify processor function
    const processor = (inputs: InputStructure) => {
        if (inputs.option === 'add') {
            return inputs.value1 + inputs.value2;
        } else if (inputs.option === 'subtract') {
            return inputs.value1 - inputs.value2;
        } else if (inputs.option === 'multiply') {
            return inputs.value1 * inputs.value2;
        } else {
            return inputs.value1 / inputs.value2;
        }
    };

    // Generate output store
    const output = generateOutput(inputs, processor);
</script>

<Node width={400} height={200} useDefaults>
    <div class="node">
        <div class="radio-group">
            <RadioGroup
                options={['subtract', 'add', 'multiply', 'divide']}
                parameterStore={$inputs.option}
            />
        </div>
        <div class="sliders">
            <Slider parameterStore={$inputs.value1} />
            <Slider parameterStore={$inputs.value2} />
        </div>
        <div class="input-anchors">
            {#each Object.entries($inputs) as [key, value] (key)}
                <Anchor {key} inputsStore={inputs} input />
            {/each}
        </div>
        <div class="output-anchors">
            <Anchor outputStore={output} output />
        </div>
    </div>
</Node>

