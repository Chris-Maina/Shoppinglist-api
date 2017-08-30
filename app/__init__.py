"""app/__init__.py"""

from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort

# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()

def create_app(config_name):
    """Initialize app"""
    from app.models import Shoppinglist
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/shoppinglists/', methods=['POST', 'GET'])
    def shoppinglists():
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
    
    @app.route('/shoppinglists/<int: id>', methods=['PUT', 'GET', 'DELETE'])
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
    return app
