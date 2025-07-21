# apiflow
Api proxy and workflow for media applications


## Stack
**worker**: Python, Peewee
**api**: Python, FastAPI, Peewee
**frontend**: Svelte 5, TailwindCSS,

all in a docker containers with docker-compose.

## Db structure

`backend/lib/db.py`

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

```json
{
    "summary": "string",
    "description": "string",
    "schema": {
        "type": "object",
        "properties": {},
        "required": []
    },
    "value": {
        "modules": [
            {
                "id": "string",
                "summary": "string",
                "value": {
                    "type": "script",
                    "path": "connector/node_path",
                    "input_transforms": {}
                }
            }
        ]
    }
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
            "default": "",
            "mapping": "output",
            "description": "The output image URL"
        }
    ]
}
```

**Declare a workflow**

The workflow will call kontext node twice,
once with prompt "Add a Hat to person",
and once with prompt "Make this a 90s cartoon"

POST /api/v1/workflows
auth: Bearer <token>
```json
{
    "name": "Replicate Flux Kontext Pro Workflow",
    "description": "A workflow that uses the Replicate Flux Kontext Pro node",
    "nodes": {
        "summary": "Replicate Flux Kontext Pro Workflow",
        "description": "A workflow that processes an image with two different prompts sequentially",
        "schema": {
            "type": "object",
            "properties": {
                "input_image": {
                    "type": "string",
                    "description": "The input image to process"
                }
            },
            "required": ["input_image"]
        },
        "value": {
            "modules": [
                {
                    "id": "add_hat_step",
                    "summary": "Add Hat to Person",
                    "value": {
                        "type": "script",
                        "path": "node/replicate_flux_kontext_pro_node_id",
                        "input_transforms": {
                            "prompt": {
                                "type": "static",
                                "value": "Add a Hat to person"
                            },
                            "input_image": {
                                "type": "javascript",
                                "expr": "flow_input.input_image"
                            },
                            "aspect_ratio": {
                                "type": "static",
                                "value": "match_input_image"
                            }
                        }
                    }
                },
                {
                    "id": "cartoon_step",
                    "summary": "Make 90s Cartoon",
                    "value": {
                        "type": "script",
                        "path": "node/replicate_flux_kontext_pro_node_id",
                        "input_transforms": {
                            "prompt": {
                                "type": "static",
                                "value": "Make this a 90s cartoon"
                            },
                            "input_image": {
                                "type": "javascript",
                                "expr": "results.add_hat_step.output_image"
                            },
                            "aspect_ratio": {
                                "type": "static",
                                "value": "match_input_image"
                            }
                        }
                    }
                }
            ]
        }
    }
}
```

## Advanced OpenFlow Features

**Conditional Processing with BranchOne:**
```json
{
    "name": "Conditional Image Processing",
    "description": "Process image based on condition",
    "nodes": {
        "summary": "Conditional Image Processing",
        "schema": {
            "type": "object",
            "properties": {
                "input_image": {"type": "string"},
                "processing_type": {"type": "string", "enum": ["cartoon", "vintage", "cyberpunk"]}
            },
            "required": ["input_image", "processing_type"]
        },
        "value": {
            "modules": [
                {
                    "id": "conditional_processing",
                    "summary": "Choose Processing Type",
                    "value": {
                        "type": "branchone",
                        "branches": [
                            {
                                "expr": "flow_input.processing_type === 'cartoon'",
                                "summary": "Cartoon Processing",
                                "modules": [
                                    {
                                        "id": "cartoon_node",
                                        "value": {
                                            "type": "script",
                                            "path": "node/replicate_flux_kontext_pro_node_id",
                                            "input_transforms": {
                                                "prompt": {"type": "static", "value": "Make this a 90s cartoon"},
                                                "input_image": {"type": "javascript", "expr": "flow_input.input_image"}
                                            }
                                        }
                                    }
                                ]
                            },
                            {
                                "expr": "flow_input.processing_type === 'vintage'",
                                "summary": "Vintage Processing",
                                "modules": [
                                    {
                                        "id": "vintage_node",
                                        "value": {
                                            "type": "script",
                                            "path": "node/replicate_flux_kontext_pro_node_id",
                                            "input_transforms": {
                                                "prompt": {"type": "static", "value": "Make this vintage style"},
                                                "input_image": {"type": "javascript", "expr": "flow_input.input_image"}
                                            }
                                        }
                                    }
                                ]
                            }
                        ],
                        "default": [
                            {
                                "id": "default_processing",
                                "value": {
                                    "type": "script",
                                    "path": "node/replicate_flux_kontext_pro_node_id",
                                    "input_transforms": {
                                        "prompt": {"type": "static", "value": "Enhance this image"},
                                        "input_image": {"type": "javascript", "expr": "flow_input.input_image"}
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }
}
```

**Parallel Processing with BranchAll:**
```json
{
    "name": "Parallel Style Processing",
    "description": "Process image with multiple styles in parallel",
    "nodes": {
        "summary": "Parallel Style Processing",
        "schema": {
            "type": "object",
            "properties": {
                "input_image": {"type": "string"}
            },
            "required": ["input_image"]
        },
        "value": {
            "modules": [
                {
                    "id": "parallel_styles",
                    "summary": "Generate Multiple Styles",
                    "value": {
                        "type": "branchall",
                        "parallel": true,
                        "branches": [
                            {
                                "summary": "Cyberpunk Style",
                                "modules": [
                                    {
                                        "id": "cyberpunk_style",
                                        "value": {
                                            "type": "script",
                                            "path": "node/replicate_flux_kontext_pro_node_id",
                                            "input_transforms": {
                                                "prompt": {"type": "static", "value": "Make this cyberpunk style"},
                                                "input_image": {"type": "javascript", "expr": "flow_input.input_image"}
                                            }
                                        }
                                    }
                                ]
                            },
                            {
                                "summary": "Vintage Style",
                                "modules": [
                                    {
                                        "id": "vintage_style",
                                        "value": {
                                            "type": "script",
                                            "path": "node/replicate_flux_kontext_pro_node_id",
                                            "input_transforms": {
                                                "prompt": {"type": "static", "value": "Make this vintage style"},
                                                "input_image": {"type": "javascript", "expr": "flow_input.input_image"}
                                            }
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }
    }
}
```

**Retry Logic:**
```json
{
    "name": "Reliable Processing",
    "description": "Process with retry logic",
    "nodes": {
        "summary": "Reliable Processing",
        "schema": {
            "type": "object",
            "properties": {
                "input_image": {"type": "string"},
                "prompt": {"type": "string"}
            },
            "required": ["input_image", "prompt"]
        },
        "value": {
            "modules": [
                {
                    "id": "reliable_processing",
                    "summary": "Process with Retry",
                    "retry": {
                        "exponential": {
                            "attempts": 3,
                            "multiplier": 2,
                            "seconds": 5
                        }
                    },
                    "value": {
                        "type": "script",
                        "path": "node/replicate_flux_kontext_pro_node_id",
                        "input_transforms": {
                            "prompt": {"type": "javascript", "expr": "flow_input.prompt"},
                            "input_image": {"type": "javascript", "expr": "flow_input.input_image"}
                        }
                    }
                }
            ]
        }
    }
}
```

## API

### Connectors
**Get all connectors**
GET /api/v1/connectors
auth: Bearer <token>
**Get a connector by ID**
GET /api/v1/connectors/{connector_id}
auth: Bearer <token>
**Create a connector**
POST /api/v1/connectors
auth: Bearer <token>
```json
{
    "name": "string",
    "base_url": "string",
    "method": "GET/POST/PUT/DELETE",
    "header": {
        "Authorization": "Bearer <token>",
        "Content-Type": "application/json"
    },
    "body": {
        "key": "value"
    }
}
```

**Update a connector**
PATCH /api/v1/connectors/{connector_id}
auth: Bearer <token>
```json
{
    "name": "string",
    "base_url": "string",
    "method": "GET/POST/PUT/DELETE",
    "header": {
        "Authorization": "Bearer <token>",
        "Content-Type": "application/json"
    },
    "body": {
        "key": "value"
    }
}
```

**Delete a connector**
DELETE /api/v1/connectors/{connector_id}
auth: Bearer <token>


### Nodes
**Get all nodes**
GET /api/v1/nodes
auth: Bearer <token>
**Get a node by ID**
GET /api/v1/nodes/{node_id}
auth: Bearer <token>
**Create a node**
POST /api/v1/nodes
auth: Bearer <token>
```json
{
    "name": "string",
    "description": "string",
    "connector_id": "connector_id",
    "input": [
        {
            "name": "string",
            "type": "string",
            "required": true,
            "default": "string",
            "value": "string",
            "description": "string"
        }
    ],
    "output": [
        {
            "name": "string",
            "type": "string",
            "default": "",
            "mapping": "output",
            "description": "string"
        }
    ]
}
```

**Update a node**
PATCH /api/v1/nodes/{node_id}
auth: Bearer <token>
```json
{
    "name": "string",
    "description": "string",
    "connector_id": "connector_id",
    "input": [
        {
            "name": "string",
            "type": "string",
            "required": true,
            "default": "string",
            "value": "string",
            "description": "string"
        }
    ],
    "output": [
        {
            "name": "string",
            "type": "string",
            "default": "",
            "mapping": "output",
            "description": "string"
        }
    ]
}
```

**Delete a node**
DELETE /api/v1/nodes/{node_id}
auth: Bearer <token>


### Workflows
**Get all workflows**
GET /api/v1/workflows
auth: Bearer <token>
**Get a workflow by ID**
GET /api/v1/workflows/{workflow_id}
auth: Bearer <token>
**Create a workflow**
POST /api/v1/workflows
auth: Bearer <token>
```json
{
    "name": "string",
    "description": "string",
    "nodes": {
        "summary": "string",
        "description": "string",
        "schema": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "value": {
            "modules": [
                {
                    "id": "string",
                    "summary": "string",
                    "value": {
                        "type": "script",
                        "path": "connector/node_path",
                        "input_transforms": {}
                    }
                }
            ]
        }
    }
}
```
**Update a workflow**
PATCH /api/v1/workflows/{workflow_id}
auth: Bearer <token>
```json
{
    "name": "string",
    "description": "string",
    "nodes": {
        "summary": "string",
        "description": "string",
        "schema": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "value": {
            "modules": [
                {
                    "id": "string",
                    "summary": "string",
                    "value": {
                        "type": "script",
                        "path": "connector/node_path",
                        "input_transforms": {}
                    }
                }
            ]
        }
    }
}
```
**Delete a workflow**
DELETE /api/v1/workflows/{workflow_id}
auth: Bearer <token>



### Execution

**Run a node**
ex: node/replicate_flux_kontext_pro_node_id

POST /api/v1/node/{node_id}/run
auth: Bearer <token>
```json
{
    "input": {
        "prompt": "Make this a 90s cartoon",
        "input_image": "https://replicate.delivery/pbxt/N55l5TWGh8mSlNzW8usReoaNhGbFwvLeZR3TX1NL4pd2Wtfv/replicate-prediction-f2d25rg6gnrma0cq257vdw2n4c.png",
        "aspect_ratio": "match_input_image"
    }
}
```

**Run a workflow**
POST /api/v1/workflow/{workflow_id}/run
auth: Bearer <token>
```json
{
    "input": {
        "input_image": "https://replicate.delivery/pbxt/N55l5TWGh8mSlNzW8usReoaNhGbFwvLeZR3TX1NL4pd2Wtfv/replicate-prediction-f2d25rg6gnrma0cq257vdw2n4c.png"
    }
}
```

Will create a job for the workflow, and run it.



### Jobs

**Get all jobs**
GET /api/v1/jobs
auth: Bearer <token>

**Get a job by ID**
GET /api/v1/jobs/{job_id}
auth: Bearer <token>

**Get jobs by workflow ID**
GET /api/v1/workflow/{workflow_id}/jobs
auth: Bearer <token>

**Cancel a job**
POST /api/v1/jobs/{job_id}/cancel
auth: Bearer <token>


### User

**Get user info**
GET /api/v1/user/{user_id}
auth: Bearer <token>

**Update user info**
PATCH /api/v1/user
auth: Bearer <token>
```json
{
    "username": "new_username",
    "email": "email",
}
```

**Reset token**
POST /api/v1/user/{user_id}/reset_token
auth: Bearer <token>

returns a new token for the user.

**Delete user account**
DELETE /api/v1/user
auth: Bearer <token>


## ENVS (.env and .env.example)
```
PUBLIC_API_URL=http://localhost:8000
ADMIN_LOGIN=admin
ADMIN_PASSWORD=admin
```


## Frontend

The frontend helps the user to create workflows, nodes, and connectors.
Also to run them, and see the results.

check `docs/svelvet.md` for more details on the node libarary used in the frontend.

Dont hesitate to create component per type of node, connector, or workflow.
ex :
- ConnectorCard.svelte
- ConnectorForm.svelte
- and so on...

**/connectors**
- List all connectors
- Create a new connector (modal)
- Edit a connector (modal)
- Delete a connector

**/nodes**
- List all nodes
- Create a new node (modal)
- Edit a node (modal)
- Delete a node

**/workflows**
- List all workflows
- Create a new workflow (modal)
  - Select nodes from a list
  - Configure input/output for each node
  - Side by side editor json editor and sveltet node preview
- Edit a workflow (modal)
- Delete a workflow

**/jobs**
- List all jobs
- View job details
  - Sveltet node preview (where we can see on which node the job is running)
- Cancel a job
- Run a job

**/user**
- List users
- View user details
- Edit user details (modal)
  - Click to reset token 
- Delete user account (modal)