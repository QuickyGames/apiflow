import peewee
from datetime import datetime
from .database import db

class User(peewee.Model):
    date_created = peewee.DateTimeField(default=datetime.now, index=True)
    date_modified = peewee.DateTimeField(default=datetime.now, index=True)
    email = peewee.CharField(unique=True, index=True)
    api_token = peewee.CharField()
    
    class Meta:
        database = db


class Workflow(peewee.Model):
    date_created = peewee.DateTimeField(default=datetime.now, index=True)
    date_modified = peewee.DateTimeField(default=datetime.now, index=True)
    runs = peewee.IntegerField(default=0, index=True)
    name = peewee.CharField(index=True)
    owner = peewee.ForeignKeyField(User, backref="workflows")
    content = peewee.TextField()

    class Meta:
        database = db

class Nodes(peewee.Model):
    date_created = peewee.DateTimeField(default=datetime.now, index=True)
    date_modified = peewee.DateTimeField(default=datetime.now, index=True)
    name = peewee.CharField(index=True)
    owner = peewee.ForeignKeyField(User, backref="nodes")
    content = peewee.TextField()

    class Meta:
        database = db

class Job(peewee.Model):
    date_created = peewee.DateTimeField(default=datetime.now, index=True)
    date_modified = peewee.DateTimeField(default=datetime.now, index=True)
    runs = peewee.IntegerField(default=0, index=True)
    name = peewee.CharField(index=True)
    status = peewee.CharField(index=True)
    owner = peewee.ForeignKeyField(User, backref="jobs")
    workflows = peewee.ManyToManyField(Workflow, backref='jobs')
    results = peewee.TextField(null=True)

    class Meta:
        database = db
