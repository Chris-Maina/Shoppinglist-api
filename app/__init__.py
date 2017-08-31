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
    from app.models import Shoppingitem
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
            regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
            if email == "":
                # check if email is empty, status code bad request 400
                response = {
                    'message': 'Please fill email field.'
                }
                return make_response(jsonify(response)), 400
            elif not re.match(regex, email):
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

    @app.route('/auth/login/', methods=['POST', 'GET'])
    def dummy_login():
        """ Handle user login"""
        if request.method == 'POST':
            email = str(request.data.get('email'))
            password = str(request.data.get('password'))
            if email == "":
                # check if email is empty, status code bad request 400
                response = {
                    'message': 'Please fill email field.'
                }
                return make_response(jsonify(response)), 400
            elif password == "":
                # check if password is empty, status code bad request 400
                response = {
                    'message': 'Please fill password field.'
                }
                return make_response(jsonify(response)), 400
            # Query to see if a user already exists
            user = User.query.filter_by(email=email).first()
            # check is user object has sth and password is correct
            if user and user.password_is_valid(password):
                # generate an access token
                access_token = user.generate_token(user.id)
                # if an access token is generated, success status_code=OK!
                if access_token:
                    response = {
                        'message': "You are logged in successfully",
                        'access_token': access_token.decode()
                    }
                    return make_response(jsonify(response)), 200
            else:
                # User does not exist, status_code=UNAUTHORIZED
                response = {
                    'message': "Invalid email or password, Please try again"
                }
                return make_response(jsonify(response)), 401
        else:
            # request method GET
            response = jsonify({"message": "To login,"
                                           "send a POST request to /auth/login/"})
            return make_response(response), 200

    @app.route('/shoppinglists/', methods=['POST', 'GET'])
    def dummy_shoppinglists():
        """ Handles POST and GET methods"""
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
         # decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                #  the user is authenticated

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
            else:
                # user_id is a string, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

    @app.route('/shoppinglists/<int:id>', methods=['PUT', 'GET', 'DELETE'])
    def dummy_shoppinglist_edit(id, **kwargs):
        """Handles shopping list CREATE, DELETE and EDIT"""
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
         # decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # the user is authenticated
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
            else:
                # user_id is a string, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

    @app.route('/shoppinglists/<int:slid>/items', methods=['POST', 'GET'])
    def dummy_shoppingitems(slid):
        """ Endpoint handles creation of shopping items"""
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                #  the user is authenticated
                if request.method == 'POST':
                    name = str(request.data.get('name'))
                    if name:
                        # there is a name, check if item exists
                        if Shoppingitem.query.filter_by(name=name, in_shoppinglist=slid).first() is not None:
                            # item exists, status code= Found
                            response = jsonify({
                                'message': "Item name already exists. Please use different name"
                            })
                            return make_response(response), 302
                        else:
                            # item does not exist, create and save the item
                            shoppingitem = Shoppingitem(
                                name=name, in_shoppinglist=slid, created_by=user_id)
                            shoppingitem.save()
                            response = jsonify({
                                "id": shoppingitem.id,
                                "name": shoppingitem.name,
                                "date_created": shoppingitem.date_created,
                                "date_modified": shoppingitem.date_modified,
                                "in_shoppinglist": slid,
                                "created_by": user_id
                            })
                            return make_response(response), 201
                    else:
                        # name is empty, status code bad request 400
                        response = {
                            'message': 'Please provide an item name.'
                        }
                        return make_response(jsonify(response)), 400

                else:
                    # request.method == 'GET'
                    # get all shopping items for a shoppinglist and user
                    items = Shoppingitem.query.filter_by(
                        in_shoppinglist=slid, created_by=user_id)
                    results = []
                    for item in items:
                        obj = {
                            "id": item.id,
                            "name": item.name,
                            "date_created": item.date_created,
                            "date_modified": item.date_modified,
                            "in_shoppinglist": slid,
                            "created_by": user_id
                        }
                        # append each item
                        results.append(obj)
                    return make_response(jsonify(results)), 200
            else:
                # user_id is a string, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

    @app.route('/shoppinglists/<int:slid>/items/<int:tid>', methods=['PUT'])
    def dummy_item_edit(tid, slid):
        """Endpoint handles editing a shopping item"""
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # retrieve  item using its ID
                item = Shoppingitem.query.filter_by(id=tid, in_shoppinglist=slid, created_by=user_id).first()
                if not item:
                    # if empty raise a 404,Not found error. No item with id=tid
                    response = {
                        'message': "No such activity"
                    }
                    return make_response(jsonify(response)), 404
                if request.method == 'PUT':
                    # obtain new name from request
                    name = str(request.data.get('name', ''))
                    if not name:
                        # no name, status code=bad request
                        response = {
                            'message': "Please enter an item name"
                        }
                        return make_response(jsonify(response)), 400
                    item.name = name
                    item.save()
                    response = jsonify({
                        "id": item.id,
                        "name": item.name,
                        "date_created": item.date_created,
                        "date_modified": item.date_modified,
                        "in_shoppinglist": item.in_shoppinglist,
                        "created_by": item.created_by
                    })
                    return make_response(response), 200
            else:
                # user_id is a string, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

    return app
