"""app/__init__.py"""
import re
import os
from datetime import datetime, timedelta
from functools import wraps
import jwt
from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
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

    def authentication(funct):
        """ Handles authentication of requests using JWT tokens"""
        @wraps(funct)
        def check(*args, **kwargs):
            """Check for the token in the Authorization header"""
            access_token = None
            if 'Authorization' in request.headers:
                # Get the access token from the header
                auth_header = request.headers.get('Authorization')
                access_token = auth_header.split(" ")[1]
                # decode the token and get the User ID
                user_id = User.decode_token(access_token)
                if not isinstance(user_id, str):
                    #  the user is authenticated
                    return funct(user_id, *args, **kwargs)
                # user_id is a string, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

            response = {
                'message': "Token is missing. Please place token in authorization header."
            }
            return make_response(jsonify(response)), 401

        return check

    @app.errorhandler(404)
    def handle_404(error):
        """Handles 404 errors"""
        response = {
            "status": 404,
            "message": "The requested {} is not found ".format(request.url)
        }
        return make_response(jsonify(response)), 404

    @app.errorhandler(405)
    def handle_405(error):
        """Handles 405 errors"""
        response = {
            "status": 405,
            "message": "Method not allowed on {} ".format(request.url)
        }
        return make_response(jsonify(response)), 405

    @app.errorhandler(500)
    def handle_500(error):
        """Handles 500 errors"""
        response = {
            "status": 500,
            "message": "There is an error at this endpoint ".format(request.url)
        }
        return make_response(jsonify(response)), 500

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
            email = str(request.data.get('email')) if request.data.get('email') else None
            password = str(request.data.get('password')) if request.data.get('password') else None
            if not email:
                # check if email is empty, status code bad request 400
                response = {
                    'message': 'Please fill email field.'
                }
                return make_response(jsonify(response)), 400
            elif not password:
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

    @app.route('/user', methods=['GET'])
    @authentication
    def dummy_user_profile(user_id):
        """ Load the user profile """
        # Query to see if a user already exists
        user = User.query.filter_by(id=user_id).first()
        if user:
            # Load the profile
            response = jsonify({
                'id': user.id,
                'email': user.email
            })
            return make_response(response), 200
        # user does not exist, status code= Not found
        response = jsonify({
            "message": "User does not exist."
        })
        return make_response(response), 404

    @app.route('/user/reset', methods=['POST'])
    def dummy_get_reset_token():
        """Allows a user to get reset token"""
        if request.method == "POST":
            email = str(request.data.get('email')) if request.data.get('email') else None
            if email:
                # email has sth
                # Query to see if a user already exists
                user = User.query.filter_by(email=email).first()
                if user:
                    # create token with email
                    # set up a payload with an expiration time
                    payload = {
                        'exp': datetime.utcnow() + timedelta(minutes=60),
                        'iat': datetime.utcnow(),
                        'sub': email
                    }

                    email_token = jwt.encode(
                        payload,
                        os.getenv('SECRET'),
                        algorithm='HS256'
                    )
                    response = {
                        "reset_token": email_token.decode()
                    }
                    return make_response(jsonify(response)), 200
                response = {
                    'message': 'User does not exist.'
                }
                return make_response(jsonify(response)), 400
            response = {
                'message': 'Please fill email field.'
            }
            return make_response(jsonify(response)), 400

    @app.route('/user/reset/password/<email_token>', methods=['PUT'])
    def dummy_reset_password(email_token):
        """"Allows a user to reset password"""
        try:
            # Decode token with our secret key
            payload = jwt.decode(email_token, os.getenv('SECRET'))
            email = payload['sub']
            # Query to see if a user already exists
            user = User.query.filter_by(email=email).first()
            if request.method == "PUT":
                password = str(request.data.get('password', '')) \
                if request.data.get('password', '') else user.password
                if len(password) < 6:
                    response = {
                        'message': 'Your password should be atleast 6 characters long.'
                    }
                    return make_response(jsonify(response)), 403
                # Update the profile
                user.email = email
                user.password = Bcrypt().generate_password_hash(password).decode()
                user.save()
                response = jsonify({
                    'message': "You have successfully changed your password"
                })
                return make_response(response), 200
        except Exception as e:
            response = {
                "message": str(e)+" in your token. Use the token provided."
            }
            return make_response(jsonify(response))

    @app.route('/user', methods=['PUT'])
    @authentication
    def dummy_update_profile(user_id):
        """Update user profile"""
        # Query to see if a user already exists
        user = User.query.filter_by(id=user_id).first()
        if user:
            # Update profile
            email = str(request.data.get('email', '')) if str(request.data.get('email', '')) \
                else user.email
            password = str(request.data.get('password', '')) \
                if str(request.data.get('password', '')) else user.password

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
            # Update the profile
            user.email = email
            user.password = Bcrypt().generate_password_hash(password).decode()
            user.save()
            response = jsonify({
                'id': user.id,
                'email': user.email,
                'message': "Successfully updated profile"
            })
            return make_response(response), 200
        else:
            # user does not exist, status code= Not found
            response = jsonify({
                "message": "User does not exist."
            })
            return make_response(response), 404

    @app.route('/shoppinglists/', methods=['GET'])
    @authentication
    def dummy_shoppinglists_get(user_id):
        """ Handles GET method"""
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

    @app.route('/shoppinglists/', methods=['POST', 'GET'])
    @authentication
    def dummy_shoppinglists(user_id):
        """ Handles POST method"""

        if request.method == "POST":
            name = str(request.data.get('name')) if request.data.get('name') else None
            if name:
                # there is a name,
                # Check for special characters
                if re.match("^[a-zA-Z0-9 _]*$", name):
                    # check if list exists
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

                # special characters exists bad request
                else:
                    response = jsonify({
                        'message': "No special characters in name"
                    })
                    return make_response(response), 400

            # no name, status code=bad request
            response = {
                "message": "Please enter a shopping list name"
            }
            return make_response(jsonify(response)), 400

    @app.route('/shoppinglists/<int:sl_id>', methods=['PUT', 'GET', 'DELETE'])
    @authentication
    def dummy_shoppinglist_edit(user_id, sl_id):
        """Handles shopping list GETTING, DELETE and EDIT"""
        # retrieve a shoppinglist by it's ID
        shoppinglist = Shoppinglist.query.filter_by(
            id=sl_id, created_by=user_id).first()
        if not shoppinglist:
            # No shopping list ,raise error 404 status code not found
            response = {
                'message': "No such shoppinglist"
            }
            return make_response(jsonify(response)), 404
        if request.method == 'DELETE':
            shoppinglist.delete()
            return {
                "message": "Shopping list {} deleted successfully".format(shoppinglist.name)
            }, 200
        elif request.method == 'PUT':
            name = str(request.data.get('name', ''))
            if name:
                # there is a name
                # Check for special characters
                if re.match("^[a-zA-Z0-9 _]*$", name):
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
                # special characters exists, bad request   
                response = jsonify({
                    'message': "No special characters in name"
                })
                return make_response(response), 400
            # no name, status code=bad request
            response = {
                "message": "Please enter a shopping list name"
            }
            return make_response(jsonify(response)), 400
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

    @app.route('/shoppinglists/<int:sl_id>/items', methods=['GET'])
    @authentication
    def dummy_shoppingitems_get(user_id, sl_id):
        """ Endpoint handles getting of shopping items"""
        if request.method == 'GET':
            # request.method == 'GET'
            # initialize search query, limit and page_no
            search_query = request.args.get("q")
            limit = request.args.get('limit')
            page_no = request.args.get('page')
            results = []
            # retrieve a shoppinglist by it's ID
            shoppinglist = Shoppinglist.query.filter_by(
                id=sl_id, created_by=user_id).first()
            if not shoppinglist:
                # No shopping list ,raise error 404 status code not found
                response = {
                    'message': "No such shoppinglist"
                }
                return make_response(jsonify(response)), 404

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
                            'price': shoppingitem.price,
                            'quantity': shoppingitem.quantity,
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
                        'name': item.name,
                        'price': item.price,
                        'quantity': item.quantity
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

    @app.route('/shoppinglists/<int:sl_id>/items', methods=['POST'])
    @authentication
    def dummy_shoppingitems(user_id, sl_id):
        """ Endpoint handles creation of shopping items"""
        if request.method == 'POST':
            name = str(request.data.get('name'))
            price = request.data.get('price')
            quantity = request.data.get('quantity')

            # retrieve a shoppinglist by it's ID
            shoppinglist = Shoppinglist.query.filter_by(
                id=sl_id, created_by=user_id).first()
            if not shoppinglist:
                # No shopping list ,raise error 404 status code not found
                response = {
                    'message': "No such shoppinglist"
                }
                return make_response(jsonify(response)), 404

            # check if price is empty or not
            if price:
                try:
                    price = int(price)
                    if price < 1:
                        response = {
                            "message": "Price value must be a positive integer"
                        }
                        return make_response(jsonify(response)), 400
                except Exception:
                    response = {
                        "message": "Invalid price value"
                    }
                    return make_response(jsonify(response)), 400
            else:
                response = {
                    "message": "Please provide a price value"
                }
                return make_response(jsonify(response)), 400

            # check if quantity is empty or not
            if quantity:
                try:
                    quantity = int(quantity)
                    if quantity < 1:
                        response = {
                            "message": "Quantity value must be a positive integer"
                        }
                        return make_response(jsonify(response)), 400
                except Exception:
                    response = {
                        "message": "Invalid quantity value"
                    }
                    return make_response(jsonify(response)), 400
            else:
                response = {
                    "message": "Please provide a quantity value"
                }
                return make_response(jsonify(response)), 400

            if name:
                # there is a name,
                # Check for special characters
                if re.match("^[a-zA-Z0-9 _]*$", name):
                    # check if item exists
                    if Shoppingitem.query.filter_by(
                            name=name, in_shoppinglist=sl_id).first() is not None:
                        # item exists, status code= Found
                        response = jsonify({
                            'message': "Item name already exists. Please use different name"
                        })
                        return make_response(response), 302

                    # item does not exist, create and save the item
                    shoppingitem = Shoppingitem(
                        name=name, price=price, quantity=quantity,
                        in_shoppinglist=sl_id, created_by=user_id)
                    shoppingitem.save()
                    response = jsonify({
                        "id": shoppingitem.id,
                        "name": shoppingitem.name,
                        "price": shoppingitem.price,
                        "quantity": shoppingitem.quantity,
                        "date_created": shoppingitem.date_created,
                        "date_modified": shoppingitem.date_modified,
                        "in_shoppinglist": sl_id,
                        "created_by": user_id
                    })
                    return make_response(response), 201
                # special characters exists, bad request
                else:
                    response = jsonify({
                        'message': "No special characters in name"
                    })
                    return make_response(response), 400

            # name is empty, status code bad request 400
            response = {
                'message': 'Please provide an item name.'
            }
            return make_response(jsonify(response)), 400

    @app.route('/shoppinglists/<int:sl_id>/items/<int:tid>', methods=['PUT'])
    @authentication
    def dummy_item_edit(user_id, tid, sl_id):
        """Endpoint handles editing a shopping item"""
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
            # obtain new name/price/quatity from request
            name = str(request.data.get('name', '')) if str(request.data.get('name', '')) \
                else item.name
            price = request.data.get('price', '') if request.data.get(
                'price', '') else item.price
            quantity = request.data.get('quantity', '') if request.data.get('quantity', '') \
                else item.quantity

            # Check for special characters
            if re.match("^[a-zA-Z0-9 _]*$", name):
                item.name = name
                item.price = price
                item.quantity = quantity
                item.save()
                response = jsonify({
                    "id": item.id,
                    "name": item.name,
                    "price": item.price,
                    "quantity": item.quantity,
                    "date_created": item.date_created,
                    "date_modified": item.date_modified,
                    "in_shoppinglist": item.in_shoppinglist,
                    "created_by": item.created_by
                })
                return make_response(response), 200
            # special characters exists, bad request
            response = jsonify({
                'message': "No special characters in name"
            })
            return make_response(response), 400

    @app.route('/shoppinglists/<int:sl_id>/items/<int:tid>', methods=['DELETE', 'GET'])
    @authentication
    def dummy_item_delete_get(user_id, tid, sl_id):
        """Endpoint handles delete and get a shopping item"""
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
                "price": item.price,
                "quantity": item.quantity,
                "date_created": item.date_created,
                "date_modified": item.date_modified,
                "in_shoppinglist": item.in_shoppinglist,
                "created_by": item.created_by
            })
            return make_response(response), 200

    return app
