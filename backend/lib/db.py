import os
import json
from datetime import datetime
from peewee import *
from playhouse.postgres_ext import PostgresqlExtDatabase, JSONField

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/apiflow')

# Parse database URL
import urllib.parse
url = urllib.parse.urlparse(DATABASE_URL)
db = PostgresqlExtDatabase(
    url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    id = AutoField()
    username = CharField(unique=True)
    email = CharField(unique=True)
    password_hash = CharField()
    api_token = CharField(unique=True)
    is_admin = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

class Connector(BaseModel):
    id = AutoField()
    name = CharField()
    header = JSONField(default=dict)
    body = JSONField(default=dict)
    base_url = CharField()
    method = CharField()
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

class Node(BaseModel):
    id = AutoField()
    name = CharField()
    description = TextField()
    connector = ForeignKeyField(Connector, backref='nodes')
    path = CharField(default='')  # Path to append to connector base_url
    input = JSONField(default=list)
    output = JSONField(default=list)
    data = JSONField(default=dict)
    body_template = JSONField(default=dict)  # Template for request body transformation
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

class Workflow(BaseModel):
    id = AutoField()
    name = CharField()
    description = TextField()
    nodes = JSONField(default=dict)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

class Job(BaseModel):
    id = AutoField()
    name = CharField()
    workflow = ForeignKeyField(Workflow, backref='jobs')
    status = CharField(default='pending')  # pending, running, completed, failed, cancelled
    retry_count = IntegerField(default=0)
    input = JSONField(default=dict)
    output = JSONField(default=dict)
    error = TextField(null=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

def create_tables():
    with db:
        db.create_tables([User, Connector, Node, Workflow, Job])
        # Run migrations after creating tables
        run_migrations()

def run_migrations():
    """Run database migrations"""
    try:
        # Check if the 'path' column exists in the Node table
        cursor = db.execute_sql("SELECT column_name FROM information_schema.columns WHERE table_name='node' AND column_name='path';")
        if not cursor.fetchone():
            print("Adding 'path' column to Node table...")
            db.execute_sql("ALTER TABLE node ADD COLUMN path VARCHAR(255) DEFAULT '';")
            print("Successfully added 'path' column to Node table.")
        else:
            print("Column 'path' already exists in Node table.")
            
        # Check if the 'body_template' column exists in the Node table
        cursor = db.execute_sql("SELECT column_name FROM information_schema.columns WHERE table_name='node' AND column_name='body_template';")
        if not cursor.fetchone():
            print("Adding 'body_template' column to Node table...")
            db.execute_sql("ALTER TABLE node ADD COLUMN body_template JSON DEFAULT '{}';")
            print("Successfully added 'body_template' column to Node table.")
        else:
            print("Column 'body_template' already exists in Node table.")
    except Exception as e:
        print(f"Migration warning: {e}")
        # Don't fail if migration has issues, just log it

def init_admin_user():
    """Initialize admin user from environment variables"""
    admin_login = os.getenv('ADMIN_LOGIN', 'admin')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin')
    
    from backend.lib.auth import hash_password, generate_api_token
    
    try:
        admin_user = User.get(User.username == admin_login)
        print(f"Admin user '{admin_login}' already exists")
        print(f"Admin API token: {admin_user.api_token}")
    except User.DoesNotExist:
        admin_user = User.create(
            username=admin_login,
            email=f"{admin_login}@apiflow.local",
            password_hash=hash_password(admin_password),
            api_token=generate_api_token(),
            is_admin=True
        )
        print(f"Created admin user '{admin_login}'")
        print(f"Admin API token: {admin_user.api_token}")
    
    return admin_user
