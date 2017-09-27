"""app/__init__.py"""
import re
from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, make_response, redirect


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
        return redirect('http://docs.shoppinglistapi3.apiary.io/')

    @app.route('/auth/register/', methods=['POST', 'GET'])
    def dummy_register():
        """Handles registration of users"""
        if request.method == 'POST':
            email = str(request.data.get('email'))
            password = str(request.data.get('password'))
            regex = r"(^[a-zA-Z0-9_.]+@[a-zA-Z0-9-]+\.[a-z]+$)"
            if not re.match(regex, email):
                # check to see if email meets the above regular expression
                response = {
                    'message': 'Please provide a valid email address.'
                }
                return make_response(jsonify(response)), 403
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

            # There is a user. Return a message user already exists
            response = {
                'message': 'User already exists. Please login.'
            }
            return make_response(jsonify(response)), 202

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

    @app.route('/shoppinglists/', methods=['GET'])
    def dummy_shoppinglists_get():
        """ Handles GET method"""
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                #  the user is authenticated
                if request.method == "GET":
                    # GET request
                    # initialize search query, limit and page_no
                    search_query = request.args.get("q")
                    limit = request.args.get('limit')
                    page_no = request.args.get('page')
                    results = []

                    if page_no:
                        try:
                            page_no = int(page_no)
                            if page_no < 1:
                                response = {
                                    "message": "Page number must be a positive integer"
                                }
                                return make_response(jsonify(response)), 400
                        except Exception:
                            response = {
                                "message": "Invalid page number"
                            }
                            return make_response(jsonify(response)), 400
                    else:
                        # default page number if no page is specified
                        page_no = 1

                    if limit:
                        try:
                            limit = int(limit)
                            if limit < 1:
                                response = {
                                    "message": "Limit value must be a positive integer"
                                }
                                return make_response(jsonify(response)), 400
                        except Exception:
                            response = {
                                "message": "Invalid limit value"
                            }
                            return make_response(jsonify(response)), 400
                    else:
                        # default limit value if no limit is specified
                        limit = 10

                    if search_query:
                        # ?q is supplied sth
                        search_results = Shoppinglist.query.filter(Shoppinglist.name.ilike(
                            '%' + search_query + '%')).filter_by(created_by=user_id).all()
                        if search_results:
                            # search_results contain sth
                            for shopping in search_results:

                                item = {
                                    'id': shopping.id,
                                    'name': shopping.name,
                                    'date_created': shopping.date_created,
                                    'date_modified': shopping.date_modified,
                                    'created_by': user_id
                                }
                                results.append(item)
                            response = jsonify(results)
                            return make_response(response), 200
                        # search_results does not contain anything, status code=Not found
                        response = {
                            'message': "Shopping list name does not exist"
                        }
                        return make_response(jsonify(response)), 404
                    else:
                        # no search query, return paginated shopping list
                        all_shopping_lists = []
                        shoppinglists = Shoppinglist.query.filter_by(
                            created_by=user_id).paginate(page_no, limit)

                        # shoppinglists contains sth
                        for item in shoppinglists.items:
                            obj = {
                                'id': item.id,
                                'name': item.name
                            }
                            all_shopping_lists.append(obj)
                        next_page = 'None'
                        prev_page = 'None'
                        if shoppinglists.has_next:
                            next_page = '/shoppinglists/' + '?limit=' + str(limit) +\
                                '&page=' + str(page_no + 1)
                        if shoppinglists.has_prev:
                            prev_page = '/shoppinglists/' + '?limit=' + str(limit) +\
                                '&page=' + str(page_no - 1)
                        response = {
                            'shopping lists': all_shopping_lists,
                            'previous page': prev_page,
                            'next page': next_page
                        }
                        return make_response(jsonify(response)), 200

            # user_id is a string, so the payload is an error message
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401

    @app.route('/shoppinglists/', methods=['POST', 'GET'])
    def dummy_shoppinglists():
        """ Handles POST method"""
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                #  the user is authenticated

                if request.method == "POST":
                    name = str(request.data.get('name'))
                    if name:
                        # there is a name, check if list exists
                        if Shoppinglist.query.filter_by(
                                name=name, created_by=user_id).first() is not None:
                            # list exists, status code= Found
                            response = jsonify({
                                'message': "List name already exists. Please use different name"
                            })
                            return make_response(response), 302

                        # list name does not exist, save
                        shoppinglist = Shoppinglist(
                            name=name, created_by=user_id)
                        shoppinglist.save()
                        response = jsonify({
                            'id': shoppinglist.id,
                            'name': shoppinglist.name,
                            'date_created': shoppinglist.date_created,
                            'date_modified': shoppinglist.date_modified,
                            'created_by': user_id
                        })
                        response.status_code = 201
                        return response

                    # no name, status code=bad request
                    response = {
                        "message": "Please enter a shopping list name"
                    }
                    return make_response(jsonify(response)), 400

            # user_id is a string, so the payload is an error message
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401

    @app.route('/shoppinglists/<int:sl_id>', methods=['PUT', 'GET', 'DELETE'])
    def dummy_shoppinglist_edit(sl_id):
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
                shoppinglist = Shoppinglist.query.filter_by(id=sl_id).first()
                if not shoppinglist:
                    # No shopping list ,raise error 404 status code not found
                    response = {
                        'message': "No such bucket"
                    }
                    return make_response(jsonify(response)), 404
                if request.method == 'DELETE':
                    shoppinglist.delete()
                    return {
                        "message": "Shopping list {} deleted successfully".format(shoppinglist.name)
                    }, 200
                elif request.method == 'PUT':
                    name = str(request.data.get('name', ''))
                    shoppinglist.name = name
                    shoppinglist.save()
                    response = jsonify({
                        'id': shoppinglist.id,
                        'name': shoppinglist.name,
                        'date_created': shoppinglist.date_created,
                        'date_modified': shoppinglist.date_modified,
                        'created_by': shoppinglist.created_by
                    })
                    response.status_code = 200
                    return response
                # GET
                response = jsonify({
                    'id': shoppinglist.id,
                    'name': shoppinglist.name,
                    'date_created': shoppinglist.date_created,
                    'date_modified': shoppinglist.date_modified,
                    'created_by': shoppinglist.created_by
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

    @app.route('/shoppinglists/<int:sl_id>/items', methods=['GET'])
    def dummy_shoppingitems_get(sl_id):
        """ Endpoint handles getting of shopping items"""
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                #  the user is authenticated
                if request.method == 'GET':
                    # request.method == 'GET'
                    # initialize search query, limit and page_no
                    search_query = request.args.get("q")
                    limit = request.args.get('limit')
                    page_no = request.args.get('page')
                    results = []

                    if page_no:
                        try:
                            page_no = int(page_no)
                            if page_no < 1:
                                response = {
                                    "message": "Page number must be a positive integer"
                                }
                                return make_response(jsonify(response)), 400
                        except Exception:
                            response = {
                                "message": "Invalid page number"
                            }
                            return make_response(jsonify(response)), 400
                    else:
                        # default page number if no page is specified
                        page_no = 1

                    if limit:
                        try:
                            limit = int(limit)
                            if limit < 1:
                                response = {
                                    "message": "Limit value must be a positive integer"
                                }
                                return make_response(jsonify(response)), 400
                        except Exception:
                            response = {
                                "message": "Invalid limit value"
                            }
                            return make_response(jsonify(response)), 400
                    else:
                        # default limit value if no limit is specified
                        limit = 10

                    if search_query:
                        # ?q is supplied sth
                        search_results = Shoppingitem.query.filter(
                            Shoppingitem.name.ilike('%' + search_query + '%')).filter_by(
                                in_shoppinglist=sl_id, created_by=user_id).all()
                        if search_results:
                            # search_results contain sth
                            for shoppingitem in search_results:

                                item = {
                                    'id': shoppingitem.id,
                                    'name': shoppingitem.name,
                                    'date_created': shoppingitem.date_created,
                                    'date_modified': shoppingitem.date_modified,
                                    'in_shoppinglist': shoppingitem.in_shoppinglist,
                                    'created_by': user_id
                                }
                                results.append(item)
                            response = jsonify(results)
                            return make_response(response), 200

                        # search_results does not contain anything, status code=Not found
                        response = {
                            'message': "Shopping item name does not exist"
                        }
                        return make_response(jsonify(response)), 404

                    else:
                        # no search query, return paginated shopping list
                        all_shopping_items = []
                        shoppingitems = Shoppingitem.query.filter_by(
                            created_by=user_id, in_shoppinglist=sl_id).paginate(page_no, limit)

                        # shoppingitems contains sth
                        for item in shoppingitems.items:
                            obj = {
                                'id': item.id,
                                'name': item.name
                            }
                            all_shopping_items.append(obj)
                        next_page = 'None'
                        prev_page = 'None'
                        if shoppingitems.has_next:
                            next_page = '/shoppinglists/{}/items?limit={}&page={}'.format(
                                int(sl_id),
                                str(limit),
                                str(page_no + 1)
                            )
                        if shoppingitems.has_prev:
                            prev_page = '/shoppinglists/{}/items?limit={}&page={}'.format(
                                int(sl_id),
                                str(limit),
                                str(page_no - 1)
                            )
                        response = {
                            'shopping items': all_shopping_items,
                            'previous page': prev_page,
                            'next page': next_page
                        }
                        return make_response(jsonify(response)), 200

            # user_id is a string, so the payload is an error message
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401

    @app.route('/shoppinglists/<int:sl_id>/items', methods=['POST'])
    def dummy_shoppingitems(sl_id):
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
                        if Shoppingitem.query.filter_by(
                                name=name, in_shoppinglist=sl_id).first() is not None:
                            # item exists, status code= Found
                            response = jsonify({
                                'message': "Item name already exists. Please use different name"
                            })
                            return make_response(response), 302

                        # item does not exist, create and save the item
                        shoppingitem = Shoppingitem(
                            name=name, in_shoppinglist=sl_id, created_by=user_id)
                        shoppingitem.save()
                        response = jsonify({
                            "id": shoppingitem.id,
                            "name": shoppingitem.name,
                            "date_created": shoppingitem.date_created,
                            "date_modified": shoppingitem.date_modified,
                            "in_shoppinglist": sl_id,
                            "created_by": user_id
                        })
                        return make_response(response), 201

                    # name is empty, status code bad request 400
                    response = {
                        'message': 'Please provide an item name.'
                    }
                    return make_response(jsonify(response)), 400

            # user_id is a string, so the payload is an error message
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401

    @app.route('/shoppinglists/<int:sl_id>/items/<int:tid>', methods=['PUT'])
    def dummy_item_edit(tid, sl_id):
        """Endpoint handles editing a shopping item"""
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # retrieve  item using its ID
                item = Shoppingitem.query.filter_by(
                    id=tid, in_shoppinglist=sl_id, created_by=user_id).first()
                if not item:
                    # if empty raise a 404,Not found error. No item with id=tid
                    response = {
                        'message': "No such item"
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

    @app.route('/shoppinglists/<int:sl_id>/items/<int:tid>', methods=['DELETE', 'GET'])
    def dummy_item_delete_get(tid, sl_id):
        """Endpoint handles delete and get a shopping item"""
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # retrieve  item using its ID
                item = Shoppingitem.query.filter_by(
                    id=tid, in_shoppinglist=sl_id, created_by=user_id).first()
                if not item:
                    # if empty raise a 404,Not found error. No item with id=tid
                    response = {
                        'message': "No such item"
                    }
                    return make_response(jsonify(response)), 404

                # handle DELETE
                elif request.method == 'DELETE':
                    item.delete()
                    response = jsonify({
                        'message': "item {} deleted".format(item.name)
                    })
                    return make_response(response), 200

                # handle GET
                elif request.method == 'GET':
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
