# apiflow
Api proxy and workflow for media applications


## Db structure

**Connectors**

- id
- name
- header: json
- body: json
- base_url: string
- method: string


**Jobs**
- id
- name
- workflow_id: foreign key to Workflows
- status: string (e.g., 'pending', 'running', 'completed', 'failed')
- retry_count: integer
- created_at: timestamp
- updated_at: timestamp
- output: json 


**Nodes**
- id
- name
- description: string
- connector_id: foreign key to Connectors
- input: json
- output: json
- data: json
- created_at: timestamp
- updated_at: timestamp

**Workflows**
- id
- name
- description: string
- nodes: json 
- created_at: timestamp
- updated_at: timestamp


## Json Schema

**Nodes**

input:
```json
[
    {
        "name": "string",
        "type": "string",
        "required": true,
        "default": "string",
        "value": "string",
        "description": "string"
    },
    {
        "name": "string",
        "type": "object",
        "required": false,
        "default": null,
        "value": {
            "key": "value"
        },
        "description": "string"
    },
    {
        "name": "string",
        "type": "array",
        "required": false,
        "default": [],
        "value": [
            "item1",
            "item2"
        ],
        "description": "string"
    }

]
```

output:
```json
[
    {
        "name": "string",
        "type": "string",
        "default": "string",
        "mapping": "string",
        "description": "string"
    },
    {
        "name": "string",
        "type": "object",
        "default": null,
        "mapping": "string",
        "description": "string"
    },
    {
        "name": "string",
        "type": "array",
        "default": [],
        "mapping": "string",
        "description": "string"
    }

]
```

**workflows**

node (Directed acyclic graph)
```json
{
    "nodes": [
        
}
```

## Json API
Each connector,node, and workflow can be declared through a JSON API.

## Use case create a Replicate workflow

**Declare a connector**

POST /api/v1/connectors
auth: Bearer <token>
```json
{
    "name": "Replicate",
    "base_url": "https://api.replicate.com/v1",
    "method": "POST",
    "header": {
    "Authorization": "Bearer $REPLICATE_API_TOKEN",
    "Content-Type": "application/json",
    "Prefer": "wait"
    },

```

**Declare a kontext pro node**



POST /api/v1/nodes
auth: Bearer <token>
```json
{
    "name": "Replicate Flux Kontext Pro",
    "description": "Replicate Flux Kontext Pro node",
    "connector_id": "replicate_connector_id",
    "input": [
        {
            "name": "prompt",
            "type": "string",
            "required": true,
            "default": "Make this a 90s cartoon",
            "value": "Make this a 90s cartoon",
            "description": "The prompt to generate the image"
        },
        {
            "name": "input_image",
            "type": "string",
            "required": true,
            "default": "https://replicate.delivery/pbxt/N55l5TWGh8mSlNzW8usReoaNhGbFwvLeZR3TX1NL4pd2Wtfv/replicate-prediction-f2d25rg6gnrma0cq257vdw2n4c.png",
            "value": "https://replicate.delivery/pbxt/N55l5TWGh8mSlNzW8usReoaNhGbFwvLeZR3TX1NL4pd2Wtfv/replicate-prediction-f2d25rg6gnrma0cq257vdw2n4c.png",
            "description": "The input image to process"
        },
        {
            "name": "aspect_ratio",
            "type": "string",
            "required": false,
            "default": "match_input_image",
            "value": "match_input_image",
            "description": "The aspect ratio of the output image"
        }
    ],
    "output": [
        {
            "name": "output_image",
            "type": "string",
            "required": true,
            "default": "",
            "mapping": "output",
            "description": "The output image URL"
        }
    ],
```

**Declare a workflow**

The workflow will call kontext node twice,
onece with promt "Add a Hat to person",
and once with prompt "Make this a 90s cartoon"

POST /api/v1/workflows
auth: Bearer <token>
```json
{
    "name": "Replicate Flux Kontext Pro Workflow",
    "description": "A workflow that uses the Replicate Flux Kontext Pro node",
    "nodes": {
        "nodes": [
