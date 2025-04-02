#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route('/')
def home():
    return ''

class CamperResource(Resource):
    
    def get(self):
        campers_dicts = [camper.to_dict(rules=('-signups',)) for camper in Camper.query.all()]

        return make_response ( campers_dicts , 200 )

    def post(self):
        json = request.get_json()
        try:
            new_camper = Camper(name=json['name'], age=json['age'])
            db.session.add(new_camper)
            db.session.commit()

            return make_response ( new_camper.to_dict() , 201 )

        except:
            return make_response ( {"errors": ["validation errors"]} , 400 )
            

class CamperByID(Resource):

    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if camper:
            return make_response ( camper.to_dict() , 200 )
        
        return make_response ( {"error": "Camper not found"} , 404 )

    def patch(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if camper:
            json = request.get_json()
            try:
                for attr, value in json.items():
                    setattr(camper, attr, value)

                db.session.add(camper)
                db.session.commit()
                return make_response ( camper.to_dict(rules=('-signups',)) , 202 )
            except:
                return make_response ( {"errors": ["validation errors"]} , 400 )

        return make_response ( {"error": "Camper not found"} , 404 )

class ActivityResource(Resource):
    
    def get(self):
        activities_dicts = [activity.to_dict(rules=('-signups',)) for activity in Activity.query.all()]

        return make_response ( activities_dicts , 200 )

class ActivityByID(Resource):

    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()
        if activity:
            db.session.delete(activity)
            db.session.commit()

            return make_response ( "" , 204 )

        return make_response ( {"error":"Activity not found"} , 404 )

class SignupResource(Resource):
    
    def post(self):
        json = request.get_json()
        try:
            new_signup = Signup(time=json['time'], camper_id=json['camper_id'], activity_id=json['activity_id'])
            db.session.add(new_signup)
            db.session.commit()

            return make_response ( new_signup.to_dict() , 201 )
        except:
            return make_response ( {"errors": ["validation errors"]} , 400 )

api.add_resource(CamperResource, '/campers')
api.add_resource(CamperByID, '/campers/<int:id>')
api.add_resource(ActivityResource, '/activities')
api.add_resource(ActivityByID, '/activities/<int:id>')
api.add_resource(SignupResource, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
