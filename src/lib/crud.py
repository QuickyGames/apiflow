from . import models, schemas

def get_user(user_id: int):
    return models.User.filter(models.User.id == user_id).first()

def get_user_by_email(email: str):
    return models.User.filter(models.User.email == email).first()

def get_users(skip: int = 0, limit: int = 100):
    return list(models.User.select().offset(skip).limit(limit))

def create_user(user: schemas.UserCreate):
    import uuid
    api_token = str(uuid.uuid4())
    db_user = models.User(email=user.email, api_token=api_token)
    db_user.save()
    return db_user

# Job CRUD operations
def get_job(job_id: int):
    return models.Job.filter(models.Job.id == job_id).first()

def get_jobs(skip: int = 0, limit: int = 100):
    return list(models.Job.select().offset(skip).limit(limit))

def create_job(job: schemas.JobCreate, owner_id: int):
    db_job = models.Job(**job.dict(), owner_id=owner_id)
    db_job.save()
    return db_job

def update_job(job_id: int, job: schemas.JobBase):
    from datetime import datetime
    db_job = get_job(job_id)
    if not db_job:
        return None
    for key, value in job.dict().items():
        setattr(db_job, key, value)
    db_job.date_modified = datetime.now()
    db_job.save()
    return db_job

def delete_job(job_id: int):
    db_job = get_job(job_id)
    if db_job:
        db_job.delete_instance()

# Workflow CRUD operations
def get_workflow(workflow_id: int):
    return models.Workflow.filter(models.Workflow.id == workflow_id).first()

def get_workflows(skip: int = 0, limit: int = 100):
    return list(models.Workflow.select().offset(skip).limit(limit))

def create_workflow(workflow: schemas.WorkflowCreate, owner_id: int):
    db_workflow = models.Workflow(**workflow.dict(), owner_id=owner_id)
    db_workflow.save()
    return db_workflow

def update_workflow(workflow_id: int, workflow: schemas.WorkflowBase):
    from datetime import datetime
    db_workflow = get_workflow(workflow_id)
    if not db_workflow:
        return None
    for key, value in workflow.dict().items():
        setattr(db_workflow, key, value)
    db_workflow.date_modified = datetime.now()
    db_workflow.save()
    return db_workflow

def delete_workflow(workflow_id: int):
    db_workflow = get_workflow(workflow_id)
    if db_workflow:
        db_workflow.delete_instance()

# Node CRUD operations
def get_node(node_id: int):
    return models.Nodes.filter(models.Nodes.id == node_id).first()

def get_nodes(skip: int = 0, limit: int = 100):
    return list(models.Nodes.select().offset(skip).limit(limit))

def create_node(node: schemas.NodeCreate, owner_id: int):
    db_node = models.Nodes(**node.dict(), owner_id=owner_id)
    db_node.save()
    return db_node

def update_node(node_id: int, node: schemas.NodeBase):
    from datetime import datetime
    db_node = get_node(node_id)
    if not db_node:
        return None
    for key, value in node.dict().items():
        setattr(db_node, key, value)
    db_node.date_modified = datetime.now()
    db_node.save()
    return db_node

def delete_node(node_id: int):
    db_node = get_node(node_id)
    if db_node:
        db_node.delete_instance()
