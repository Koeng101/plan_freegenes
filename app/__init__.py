from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)


from flask_restplus import Api, Resource, fields
from flask.views import MethodView

from flask_migrate import Migrate

from sqlalchemy.dialects.postgresql import UUID
import sqlalchemy
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, abort, request, jsonify, g, url_for, Response
import uuid
from flask_cors import CORS


from .crud import *

###########
# Env var #
###########

API_TITLE = os.environ['API_TITLE']
API_DESCRIPTION = os.environ['API_DESCRIPTION']
URL = os.environ['URL']

#########
# State #
#########

db = SQLAlchemy()

class Plan(db.Model):
    __tablename__ = 'plans'
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False,default=sqlalchemy.text("uuid_generate_v4()"), primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    name = db.Column(db.String())
    description = db.Column(db.String())

    status = db.Column(db.String) # planned, tested, executed, cancelled
    plan = db.Column(db.JSON, nullable=False)

    def toJSON(self,full=None):
        return {'uuid':self.uuid, 'time_created':self.time_created.isoformat(),'time_updated':self.time_updated.isoformat(), 'name':self.name, 'description':self.description, 'status':self.status, 'plan':self.plan}

##########
# Routes #
##########

ns_plan = Namespace('plans', description='Plan namespace')
plan_model = ns_plan.model("plan", {
    "name": fields.String(),
    "description": fields.String(),
    "status": fields.String(),
    "plan": fields.Raw,
    })
CRUD(ns_plan,Plan,plan_model,'plan')


###############
# Generic app #
###############

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = URL
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# extensions
CORS(app)
db.init_app(app)
auth = HTTPBasicAuth()
authorizations = {
        'token': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'token'}
        }

api = Api(app, version='.1', title=API_TITLE,
            description=API_DESCRIPTION,
            authorizations=authorizations
            )
migrate = Migrate(app, db)

for namespace in [ns_token,ns_plan]:
    api.add_namespace(namespace)

if __name__ == '__main__':
    app.run(host='0.0.0.0')

