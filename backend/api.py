import os
import asyncio
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime

from backend.lib.db import (
    db, create_tables, init_admin_user,
    User, Connector, Node, Workflow, Job
)
from backend.lib.auth import (
    get_current_user, get_admin_user, 
    hash_password, generate_api_token
)
from backend.lib.node import execute_node
from backend.lib.workflow import execute_workflow

# Pydantic models
class ConnectorCreate(BaseModel):
    name: str
    base_url: str
    method: str = "GET"
    header: dict = Field(default_factory=dict)
    body: dict = Field(default_factory=dict)

class ConnectorUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    method: Optional[str] = None
    header: Optional[dict] = None
    body: Optional[dict] = None

class NodeCreate(BaseModel):
    name: str
    description: str
    connector_id: int
    input: list = Field(default_factory=list)
    output: list = Field(default_factory=list)
    data: dict = Field(default_factory=dict)

class NodeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    connector_id: Optional[int] = None
    input: Optional[list] = None
    output: Optional[list] = None
    data: Optional[dict] = None

class WorkflowCreate(BaseModel):
    name: str
    description: str
    nodes: dict

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: Optional[dict] = None

class NodeRunRequest(BaseModel):
    input: dict = Field(default_factory=dict)

class WorkflowRunRequest(BaseModel):
    input: dict = Field(default_factory=dict)

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    api_token: str
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Initialize FastAPI app
app = FastAPI(title="APIFlow", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
async def startup():
    # Create tables
    create_tables()
    
    # Initialize admin user
    init_admin_user()
    
    print("APIFlow API started successfully!")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Connector endpoints
@app.get("/api/v1/connectors", response_model=List[dict])
async def get_connectors(current_user: User = Depends(get_current_user)):
    connectors = list(Connector.select())
    return [
        {
            "id": c.id,
            "name": c.name,
            "base_url": c.base_url,
            "method": c.method,
            "header": c.header,
            "body": c.body,
            "created_at": c.created_at,
            "updated_at": c.updated_at
        }
        for c in connectors
    ]

@app.get("/api/v1/connectors/{connector_id}")
async def get_connector(connector_id: int, current_user: User = Depends(get_current_user)):
    try:
        connector = Connector.get(Connector.id == connector_id)
        return {
            "id": connector.id,
            "name": connector.name,
            "base_url": connector.base_url,
            "method": connector.method,
            "header": connector.header,
            "body": connector.body,
            "created_at": connector.created_at,
            "updated_at": connector.updated_at
        }
    except Connector.DoesNotExist:
        raise HTTPException(status_code=404, detail="Connector not found")

@app.post("/api/v1/connectors", status_code=201)
async def create_connector(
    connector: ConnectorCreate,
    current_user: User = Depends(get_current_user)
):
    new_connector = Connector.create(
        name=connector.name,
        base_url=connector.base_url,
        method=connector.method,
        header=connector.header,
        body=connector.body
    )
    return {
        "id": new_connector.id,
        "name": new_connector.name,
        "base_url": new_connector.base_url,
        "method": new_connector.method,
        "header": new_connector.header,
        "body": new_connector.body,
        "created_at": new_connector.created_at,
        "updated_at": new_connector.updated_at
    }

@app.patch("/api/v1/connectors/{connector_id}")
async def update_connector(
    connector_id: int,
    update: ConnectorUpdate,
    current_user: User = Depends(get_current_user)
):
    try:
        connector = Connector.get(Connector.id == connector_id)
        
        if update.name is not None:
            connector.name = update.name
        if update.base_url is not None:
            connector.base_url = update.base_url
        if update.method is not None:
            connector.method = update.method
        if update.header is not None:
            connector.header = update.header
        if update.body is not None:
            connector.body = update.body
        
        connector.save()
        
        return {
            "id": connector.id,
            "name": connector.name,
            "base_url": connector.base_url,
            "method": connector.method,
            "header": connector.header,
            "body": connector.body,
            "created_at": connector.created_at,
            "updated_at": connector.updated_at
        }
    except Connector.DoesNotExist:
        raise HTTPException(status_code=404, detail="Connector not found")

@app.delete("/api/v1/connectors/{connector_id}", status_code=204)
async def delete_connector(
    connector_id: int,
    current_user: User = Depends(get_current_user)
):
    try:
        connector = Connector.get(Connector.id == connector_id)
        connector.delete_instance()
    except Connector.DoesNotExist:
        raise HTTPException(status_code=404, detail="Connector not found")

# Node endpoints
@app.get("/api/v1/nodes", response_model=List[dict])
async def get_nodes(current_user: User = Depends(get_current_user)):
    nodes = list(Node.select())
    return [
        {
            "id": n.id,
            "name": n.name,
            "description": n.description,
            "connector_id": n.connector.id,
            "input": n.input,
            "output": n.output,
            "data": n.data,
            "created_at": n.created_at,
            "updated_at": n.updated_at
        }
        for n in nodes
    ]

@app.get("/api/v1/nodes/{node_id}")
async def get_node(node_id: int, current_user: User = Depends(get_current_user)):
    try:
        node = Node.get(Node.id == node_id)
        return {
            "id": node.id,
            "name": node.name,
            "description": node.description,
            "connector_id": node.connector.id,
            "input": node.input,
            "output": node.output,
            "data": node.data,
            "created_at": node.created_at,
            "updated_at": node.updated_at
        }
    except Node.DoesNotExist:
        raise HTTPException(status_code=404, detail="Node not found")

@app.post("/api/v1/nodes", status_code=201)
async def create_node(
    node: NodeCreate,
    current_user: User = Depends(get_current_user)
):
    try:
        connector = Connector.get(Connector.id == node.connector_id)
    except Connector.DoesNotExist:
        raise HTTPException(status_code=400, detail="Connector not found")
    
    new_node = Node.create(
        name=node.name,
        description=node.description,
        connector=connector,
        input=node.input,
        output=node.output,
        data=node.data
    )
    
    return {
        "id": new_node.id,
        "name": new_node.name,
        "description": new_node.description,
        "connector_id": new_node.connector.id,
        "input": new_node.input,
        "output": new_node.output,
        "data": new_node.data,
        "created_at": new_node.created_at,
        "updated_at": new_node.updated_at
    }

@app.patch("/api/v1/nodes/{node_id}")
async def update_node(
    node_id: int,
    update: NodeUpdate,
    current_user: User = Depends(get_current_user)
):
    try:
        node = Node.get(Node.id == node_id)
        
        if update.name is not None:
            node.name = update.name
        if update.description is not None:
            node.description = update.description
        if update.connector_id is not None:
            try:
                connector = Connector.get(Connector.id == update.connector_id)
                node.connector = connector
            except Connector.DoesNotExist:
                raise HTTPException(status_code=400, detail="Connector not found")
        if update.input is not None:
            node.input = update.input
        if update.output is not None:
            node.output = update.output
        if update.data is not None:
            node.data = update.data
        
        node.save()
        
        return {
            "id": node.id,
            "name": node.name,
            "description": node.description,
            "connector_id": node.connector.id,
            "input": node.input,
            "output": node.output,
            "data": node.data,
            "created_at": node.created_at,
            "updated_at": node.updated_at
        }
    except Node.DoesNotExist:
        raise HTTPException(status_code=404, detail="Node not found")

@app.delete("/api/v1/nodes/{node_id}", status_code=204)
async def delete_node(
    node_id: int,
    current_user: User = Depends(get_current_user)
):
    try:
        node = Node.get(Node.id == node_id)
        node.delete_instance()
    except Node.DoesNotExist:
        raise HTTPException(status_code=404, detail="Node not found")

@app.post("/api/v1/node/{node_id}/run")
async def run_node(
    node_id: int,
    request: NodeRunRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        result = execute_node(node_id, request.input)
        return {"status": "success", "output": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Workflow endpoints
@app.get("/api/v1/workflows", response_model=List[dict])
async def get_workflows(current_user: User = Depends(get_current_user)):
    workflows = list(Workflow.select())
    return [
        {
            "id": w.id,
            "name": w.name,
            "description": w.description,
            "nodes": w.nodes,
            "created_at": w.created_at,
            "updated_at": w.updated_at
        }
        for w in workflows
    ]

@app.get("/api/v1/workflows/{workflow_id}")
async def get_workflow(workflow_id: int, current_user: User = Depends(get_current_user)):
    try:
        workflow = Workflow.get(Workflow.id == workflow_id)
        return {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "nodes": workflow.nodes,
            "created_at": workflow.created_at,
            "updated_at": workflow.updated_at
        }
    except Workflow.DoesNotExist:
        raise HTTPException(status_code=404, detail="Workflow not found")

@app.post("/api/v1/workflows", status_code=201)
async def create_workflow(
    workflow: WorkflowCreate,
    current_user: User = Depends(get_current_user)
):
    new_workflow = Workflow.create(
        name=workflow.name,
        description=workflow.description,
        nodes=workflow.nodes
    )
    
    return {
        "id": new_workflow.id,
        "name": new_workflow.name,
        "description": new_workflow.description,
        "nodes": new_workflow.nodes,
        "created_at": new_workflow.created_at,
        "updated_at": new_workflow.updated_at
    }

@app.patch("/api/v1/workflows/{workflow_id}")
async def update_workflow(
    workflow_id: int,
    update: WorkflowUpdate,
    current_user: User = Depends(get_current_user)
):
    try:
        workflow = Workflow.get(Workflow.id == workflow_id)
        
        if update.name is not None:
            workflow.name = update.name
        if update.description is not None:
            workflow.description = update.description
        if update.nodes is not None:
            workflow.nodes = update.nodes
        
        workflow.save()
        
        return {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "nodes": workflow.nodes,
            "created_at": workflow.created_at,
            "updated_at": workflow.updated_at
        }
    except Workflow.DoesNotExist:
        raise HTTPException(status_code=404, detail="Workflow not found")

@app.delete("/api/v1/workflows/{workflow_id}", status_code=204)
async def delete_workflow(
    workflow_id: int,
    current_user: User = Depends(get_current_user)
):
    try:
        workflow = Workflow.get(Workflow.id == workflow_id)
        workflow.delete_instance()
    except Workflow.DoesNotExist:
        raise HTTPException(status_code=404, detail="Workflow not found")

@app.post("/api/v1/workflow/{workflow_id}/run")
async def run_workflow(
    workflow_id: int,
    request: WorkflowRunRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        job = await execute_workflow(workflow_id, request.input)
        return {
            "status": "success",
            "job_id": job.id,
            "job_status": job.status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Job endpoints
@app.get("/api/v1/jobs", response_model=List[dict])
async def get_jobs(current_user: User = Depends(get_current_user)):
    jobs = list(Job.select().order_by(Job.created_at.desc()))
    return [
        {
            "id": j.id,
            "name": j.name,
            "workflow_id": j.workflow.id,
            "workflow_name": j.workflow.name,
            "status": j.status,
            "retry_count": j.retry_count,
            "input": j.input,
            "output": j.output,
            "error": j.error,
            "created_at": j.created_at,
            "updated_at": j.updated_at
        }
        for j in jobs
    ]

@app.get("/api/v1/jobs/{job_id}")
async def get_job(job_id: int, current_user: User = Depends(get_current_user)):
    try:
        job = Job.get(Job.id == job_id)
        return {
            "id": job.id,
            "name": job.name,
            "workflow_id": job.workflow.id,
            "workflow_name": job.workflow.name,
            "status": job.status,
            "retry_count": job.retry_count,
            "input": job.input,
            "output": job.output,
            "error": job.error,
            "created_at": job.created_at,
            "updated_at": job.updated_at
        }
    except Job.DoesNotExist:
        raise HTTPException(status_code=404, detail="Job not found")

@app.get("/api/v1/workflow/{workflow_id}/jobs", response_model=List[dict])
async def get_workflow_jobs(
    workflow_id: int,
    current_user: User = Depends(get_current_user)
):
    jobs = list(Job.select().where(Job.workflow == workflow_id).order_by(Job.created_at.desc()))
    return [
        {
            "id": j.id,
            "name": j.name,
            "workflow_id": j.workflow.id,
            "workflow_name": j.workflow.name,
            "status": j.status,
            "retry_count": j.retry_count,
            "input": j.input,
            "output": j.output,
            "error": j.error,
            "created_at": j.created_at,
            "updated_at": j.updated_at
        }
        for j in jobs
    ]

@app.post("/api/v1/jobs/{job_id}/cancel")
async def cancel_job(job_id: int, current_user: User = Depends(get_current_user)):
    try:
        job = Job.get(Job.id == job_id)
        if job.status in ['pending', 'running']:
            job.status = 'cancelled'
            job.save()
            return {"status": "success", "message": "Job cancelled"}
        else:
            return {"status": "error", "message": f"Cannot cancel job with status: {job.status}"}
    except Job.DoesNotExist:
        raise HTTPException(status_code=404, detail="Job not found")

# User endpoints
@app.get("/api/v1/user/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, current_user: User = Depends(get_admin_user)):
    try:
        user = User.get(User.id == user_id)
        return UserResponse.from_orm(user)
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

@app.patch("/api/v1/user")
async def update_user(
    update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    if update.username is not None:
        # Check if username already exists
        existing = User.select().where(
            (User.username == update.username) & (User.id != current_user.id)
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")
        current_user.username = update.username
    
    if update.email is not None:
        # Check if email already exists
        existing = User.select().where(
            (User.email == update.email) & (User.id != current_user.id)
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")
        current_user.email = update.email
    
    current_user.save()
    return UserResponse.from_orm(current_user)

@app.post("/api/v1/user/{user_id}/reset_token")
async def reset_user_token(user_id: int, current_user: User = Depends(get_admin_user)):
    try:
        user = User.get(User.id == user_id)
        user.api_token = generate_api_token()
        user.save()
        return {"status": "success", "new_token": user.api_token}
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

@app.delete("/api/v1/user", status_code=204)
async def delete_user(current_user: User = Depends(get_current_user)):
    current_user.delete_instance()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
