import time
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from .lib import crud, database, models, schemas
from .lib.database import db_state_default

# Create database tables
database.db.connect()
database.db.create_tables([
    models.User,
    models.Job,
    models.Workflow,
    models.Nodes
])
database.db.close()

templates = Jinja2Templates(directory="src/templates")
app = FastAPI()
sleep_time = 10

async def reset_db_state():
    database.db._state._state.set(db_state_default.copy())
    database.db._state.reset()

def get_db(db_state=Depends(reset_db_state)):
    try:
        database.db.connect()
        yield
    finally:
        if not database.db.is_closed():
            database.db.close()

@app.post("/users/", response_model=schemas.User, dependencies=[Depends(get_db)])
def create_user(user: schemas.UserCreate):
    db_user = crud.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(user=user)

@app.get("/users/", response_model=List[schemas.User], dependencies=[Depends(get_db)])
def read_users(skip: int = 0, limit: int = 100):
    users = crud.get_users(skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User, dependencies=[Depends(get_db)])
def read_user(user_id: int):
    db_user = crud.get_user(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/users/{user_id}", dependencies=[Depends(get_db)])
def delete_user(user_id: int):
    crud.delete_user(user_id=user_id)

# Job endpoints
@app.post("/jobs/", response_model=schemas.Job, dependencies=[Depends(get_db)])
def create_job(job: schemas.JobCreate, owner_id: int):
    return crud.create_job(job=job, owner_id=owner_id)

@app.get("/jobs/", response_model=List[schemas.Job], dependencies=[Depends(get_db)])
def read_jobs(skip: int = 0, limit: int = 100):
    jobs = crud.get_jobs(skip=skip, limit=limit)
    return jobs

@app.get("/jobs/{job_id}", response_model=schemas.Job, dependencies=[Depends(get_db)])
def read_job(job_id: int):
    db_job = crud.get_job(job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job

@app.put("/jobs/{job_id}", response_model=schemas.Job, dependencies=[Depends(get_db)])
def update_job(job_id: int, job: schemas.JobBase):
    db_job = crud.update_job(job_id=job_id, job=job)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job

@app.delete("/jobs/{job_id}", dependencies=[Depends(get_db)])
def delete_job(job_id: int):
    crud.delete_job(job_id=job_id)

# Workflow endpoints
@app.post("/workflows/", response_model=schemas.Workflow, dependencies=[Depends(get_db)])
def create_workflow(workflow: schemas.WorkflowCreate, owner_id: int):
    return crud.create_workflow(workflow=workflow, owner_id=owner_id)

@app.get("/workflows/", response_model=List[schemas.Workflow], dependencies=[Depends(get_db)])
def read_workflows(skip: int = 0, limit: int = 100):
    workflows = crud.get_workflows(skip=skip, limit=limit)
    return workflows

@app.get("/workflows/{workflow_id}", response_model=schemas.Workflow, dependencies=[Depends(get_db)])
def read_workflow(workflow_id: int):
    db_workflow = crud.get_workflow(workflow_id=workflow_id)
    if db_workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return db_workflow

@app.put("/workflows/{workflow_id}", response_model=schemas.Workflow, dependencies=[Depends(get_db)])
def update_workflow(workflow_id: int, workflow: schemas.WorkflowBase):
    db_workflow = crud.update_workflow(workflow_id=workflow_id, workflow=workflow)
    if db_workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return db_workflow

@app.delete("/workflows/{workflow_id}", dependencies=[Depends(get_db)])
def delete_workflow(workflow_id: int):
    crud.delete_workflow(workflow_id=workflow_id)

# Node endpoints
@app.post("/nodes/", response_model=schemas.Node, dependencies=[Depends(get_db)])
def create_node(node: schemas.NodeCreate, owner_id: int):
    return crud.create_node(node=node, owner_id=owner_id)

@app.get("/nodes/", response_model=List[schemas.Node], dependencies=[Depends(get_db)])
def read_nodes(skip: int = 0, limit: int = 100):
    nodes = crud.get_nodes(skip=skip, limit=limit)
    return nodes

@app.get("/nodes/{node_id}", response_model=schemas.Node, dependencies=[Depends(get_db)])
def read_node(node_id: int):
    db_node = crud.get_node(node_id=node_id)
    if db_node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    return db_node

@app.put("/nodes/{node_id}", response_model=schemas.Node, dependencies=[Depends(get_db)])
def update_node(node_id: int, node: schemas.NodeBase):
    db_node = crud.update_node(node_id=node_id, node=node)
    if db_node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    return db_node

@app.delete("/nodes/{node_id}", dependencies=[Depends(get_db)])
def delete_node(node_id: int):
    crud.delete_node(node_id=node_id)

@app.get("/slowusers/", response_model=List[schemas.User], dependencies=[Depends(get_db)])
def read_slow_users(skip: int = 0, limit: int = 100):
    global sleep_time
    sleep_time = max(0, sleep_time - 1)
    time.sleep(sleep_time)  # Fake long processing request
    users = crud.get_users(skip=skip, limit=limit)
    return users


@app.get("/dashboard/debug", response_class=HTMLResponse)
async def get_crud_template(request: Request):
    return templates.TemplateResponse("crud.html", {"request": request})
