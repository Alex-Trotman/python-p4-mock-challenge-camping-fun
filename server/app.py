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

api = Api(app)  # Initialize the Api


@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        try:
            campers = Camper.query.all()
            # campers = [ c.to_dict( only=("id", "name", "age")) for c in Camper.query.all()  ]
            new_campers = []
            for c in campers:
                new_campers.append(c.to_dict(only=("id", "name", "age")))            
            return new_campers, 200

        except: 
            return {"error": "Bad request"}, 400

    def post(self):
        data = request.get_json()
        errors = []

        # Validate name
        if 'name' not in data or not data['name']:
            errors.append("Name must not be empty")
        
        # Validate age
        if 'age' not in data or not (8 <= data['age'] <= 18):
            errors.append("Age must be between 8 and 18")
        
        if errors:
            return {"errors": errors}, 400

        new_camper = Camper(name=data['name'], age=data['age'])
        db.session.add(new_camper)
        db.session.commit()

        return new_camper.to_dict(), 201
        
    
        
api.add_resource(Campers, '/campers')

class CampersById(Resource):
    
    def get(self, id):
        # pass
        try: 
            camper = Camper.query.filter(Camper.id == id).first() #.to_dict() # only=("id", "name", "age", "activities")
            
            # print(camper)
            return camper.to_dict(), 200
        except: 
            return {"error": "Camper not found"}, 404

    def patch(self, id):
        camper = Camper.query.filter(Camper.id == id).one_or_none()

        if camper is None:
            return {'error': 'Camper not found'}, 404

        fields = request.get_json()

        try:
            setattr(camper, 'name', fields['name'])
            setattr(camper, 'age', fields['age'])
            db.session.add(camper)
            db.session.commit()

            return camper.to_dict(rules=('-signups',)), 202

        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)
        
class Activities(Resource):
    def get(self):
        activities = [activity.to_dict(rules=('-signups',)) for activity in Activity.query.all()]
        return activities, 200

class ActivititesById(Resource):

    def delete(self, id):
        activity = Activity.query.filter_by(id=id).one_or_none()

        if activity:
            db.session.delete(activity)
            db.session.commit()

            return make_response({}, 204)

        return make_response({"error": "Activity not found"}, 404)

class Signups(Resource):

    def post(self):
        try:
            signup = Signup(
                time=request.json["time"],
                camper_id=request.json["camper_id"],
                activity_id=request.json["activity_id"]
            )

            db.session.add(signup)
            db.session.commit()

            return make_response(signup.to_dict(), 201)

        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(Signups, "/signups")
api.add_resource(ActivititesById, "/activities/<int:id>")
api.add_resource(Activities, "/activities")
api.add_resource(CampersById, "/campers/<int:id>")


if __name__ == '__main__':
    app.run(port=5555, debug=True)
