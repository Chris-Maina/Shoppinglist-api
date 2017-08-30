"""app/__init__.py"""

from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, make_response
import re

# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()


def create_app(config_name):
    """Initialize app"""
    from app.models import Shoppinglist
    from app.models import User
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/')
    def dummy_index():
        """Index page"""
        return jsonify({"message": "Welcome to the Shoppinglist API."
                                   " Register a new user by sending a"
                                   " POST request to /auth/register/. "
                                   "Login by sending a POST request to"
                                   " /auth/login/ to get started."})

    @app.route('/auth/register/', methods=['POST', 'GET'])
    def dummy_register():
        """Handles registration of users"""
        if request.method == 'POST':
            email = str(request.data.get('email'))
            password = str(request.data.get('password'))
            if email == "":
                # check if email is empty, status code bad request 400
                response = {
                    'message': 'Please fill email field.'
                }
                return make_response(jsonify(response)), 400
            elif not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
                # check to see if email meets the above regular expression
                response = {
                    'message': 'Please provide a valid email address.'
                }
                return make_response(jsonify(response)), 403
            elif password == "":
                # check if password is empty, status code bad request 400
                response = {
                    'message': 'Please fill password field.'
                }
                return make_response(jsonify(response)), 400
            elif len(password) < 6:
                response = {
                    'message': 'Your password should be atleast 6 characters long.'
                }
                return make_response(jsonify(response)), 403

            # Query to see if a user already exists
            user = User.query.filter_by(email=email).first()
            if not user:
                # No user, so register
                try:
                    # Register user
                    email = request.data['email']
                    password = request.data['password']
                    user = User(email=email, password=password)
                    user.save()
                    response = {
                        'message': 'You have been registered successfully. Please login'
                    }
                    # return the response and a status code 201 (created)
                    return make_response(jsonify(response)), 201
                except Exception as e:
                    # when there is an error, return error as message
                    response = {
                        'message': str(e)
                    }
                    return make_response(jsonify(response)), 401
            else:
                # There is a user. Return a message user already exists
                response = {
                    'message': 'User already exists. Please login.'
                }
                return make_response(jsonify(response)), 202
        else:
            # request method GET
            response = jsonify({"message": "To register,"
                                           "send a POST request with email and password"
                                           " to /auth/register/"})
            return make_response(response), 200


    @app.route('/shoppinglists/', methods=['POST', 'GET'])
    def dummy_shoppinglists():
        """ Handles POST and GET methods"""
        if request.method == "POST":
            name = str(request.data.get('name', ''))
            if name:
                shoppinglist = Shoppinglist(name=name)
                shoppinglist.save()
                response = jsonify({
                    'id': shoppinglist.id,
                    'name': shoppinglist.name,
                    'date_created': shoppinglist.date_created,
                    'date_modified': shoppinglist.date_modified
                })
                response.status_code = 201
                return response
        else:
            # GET
            shoppinglists = Shoppinglist.get_all()
            results = []
            for shoplist in shoppinglists:
                item = {
                    'id': shoplist.id,
                    'name': shoplist.name,
                    'date_created': shoplist.date_created,
                    'date_modified': shoplist.date_modified
                }
                results.append(item)
            response = jsonify(results)
            response.status_code = 200
            return response

    @app.route('/shoppinglists/<int:id>', methods=['PUT', 'GET', 'DELETE'])
    def shoppinglist_edit(id, **kwargs):
        # retrieve a shoppinglist by it's ID
        shoppinglist = Shoppinglist.query.filter_by(id=id).first()
        if not shoppinglist:
            # No shopping list ,raise error 404 status code not found
            abort(404)
        if request.method == 'DELETE':
            shoppinglist.delete()
            return {
                "message": "Shopping list {} deleted successfully".format(shoppinglist.id)
            }, 200
        elif request.method == 'PUT':
            name = str(request.data.get('name', ''))
            shoppinglist.name = name
            shoppinglist.save()
            response = jsonify({
                'id': shoppinglist.id,
                'name': shoppinglist.name,
                'date_created': shoppinglist.date_created,
                'date_modified': shoppinglist.date_modified
            })
            response.status_code = 200
            return response
        else:
            # GET
            response = jsonify({
                'id': shoppinglist.id,
                'name': shoppinglist.name,
                'date_created': shoppinglist.date_created,
                'date_modified': shoppinglist.date_modified
            })
            response.status_code = 200
            return response

    return app
