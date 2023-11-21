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

migrate = Migrate(app, db, render_as_batch=True)

db.init_app(app)

api = Api(app)

class Home(Resource):
    def get(self):
        response_dict = {
            'message': 'Welcome to Camping Fun'
        }
        return make_response(response_dict, 200, )

api.add_resource(Home, '/')

class Campers(Resource):
    def get(self):
        campers = [c.to_dict(only=('id','name','age')) for c in Camper.query.all()]
        return make_response(
            campers,
            200
        )
    
    def post(self):
        try:
            params = request.json

            if 'name' not in params or 'age' not in params:
                return make_response({'error': 'Name and age are required fields.'}, 400)

            new_camper = Camper(name=params['name'], age=params['age'])

            db.session.add(new_camper)
            db.session.commit()

            return make_response(new_camper.to_dict(), 201)
            
        except ValueError as v_error:
            return make_response({'error': [str(v_error)]}, 422)
        except Exception as e:
            print(f"Exception during POST request: {str(e)}")
            return make_response({'error': 'Internal Server Error'}, 500)


api.add_resource(Campers, '/campers')

class CamperByID(Resource):
    def get(self, id):
        camper = Camper.query.get( id )
        if not camper:
            return make_response({ 'error': 'Camper not found'}, 404)
        return make_response(camper.to_dict(), 200)

    def patch(self, id):
        camper = Camper.query.get( id )
        if not camper:
            return make_response({ 'error': 'Camper not found.' }, 404)
        params = request.json
        for attr in params:
            try:
                setattr( camper, attr, params[attr] )
            except ValueError as v_error:
                return make_response({'error':[str(v_error)]}, 422)
        db.session.commit()
        return make_response( camper.to_dict(only=('id', 'name', 'age')), 200)

api.add_resource(CamperByID, '/campers/<int:id>')

class Activities(Resource):
    def get(self):
        activities = [a.to_dict(only=('id','name','difficulty')) for a in Activity.query.all()]
        return make_response(
            activities,
            200
        )
api.add_resource(Activities, '/activities')

class ActivityByID(Resource):
    def get(self, id):
        activity = Activity.query.get( id )
        if not activity:
            return make_response({ 'error': 'Activity not found'}, 404)
        return make_response(activity.to_dict(), 200)

    def delete(self, id):
        activity = Activity.query.get(id)
        if not activity:
            return make_response({'error': 'activity not found'}, 404)
        db.session.delete(activity)
        db.session.commit()
        return make_response('', 204)
api.add_resource(ActivityByID, '/activities/<int:id>')

class Signups(Resource):
    def get(self):
        signups = [s.to_dict(only=('camper_id', 'activity_id', 'time')) for s in Signup.query.all()]
        return make_response(
            signups,
            200
        )
    
    def post(self):
        try:
            params = request.get_json()

            required_fields= ['camper_id', 'activity_id', 'time']
            if not all(field in params for field in required_fields):
                return make_response({'error': 'Camper ID, Activity ID, and Time are required fields.'}, 400)

            camper = Camper.query.get(params['camper_id'])
            activity = Activity.query.get(params['activity_id'])

            if not camper or not activity:
                return make_response({'error': 'Camper or activity not found.'})
            
            new_signup = Signup(
                camper=camper,
                activity=activity,
                time=params['time']
            )

            db.session.add(new_signup)
            db.session.commit()

            return make_response(new_signup.to_dict(), 201)

        except ValueError as v_error:
            return make_response({'error': [str(v_error)]}, 422)
        except Exception as e:
            print(f"Exception during POST request: {str(e)}")
            return make_response({'error': 'Internal Server Error'}, 500)

api.add_resource(Signups, '/signups')



if __name__ == '__main__':
    app.run(port=5555, debug=True)
