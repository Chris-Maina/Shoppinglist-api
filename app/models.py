""" models.py """
import jwt
import os
from datetime import datetime, timedelta
from app import db
from flask_bcrypt import Bcrypt

SECRET_KEY = os.getenv('SECRET')


class User(db.Model):
    """Class represents Users table"""
    __tablename__ = 'users'

    # Define columns for users table
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    shoppinglists = db.relationship(
        'Shoppinglist', order_by='Shoppinglist.id', cascade="all, delete-orphan")
    shoppingitems = db.relationship(
        'Shoppingitem', order_by='Shoppingitem.id', cascade='all, delete-orphan')

    def __init__(self, email, password):
        """Initialize the user with an email and password."""
        self.email = email
        self.password = Bcrypt().generate_password_hash(password).decode()

    def password_is_valid(self, password):
        """ Check password against it's hash to validate user's password"""
        return Bcrypt().check_password_hash(self.password, password)

    def save(self):
        """ Save a user to a db"""
        db.session.add(self)
        db.session.commit()

    def generate_token(self, user_id):
        """Code to generate and encode a token before its sent to user"""
        try:
            # set up a payload with an expiration time
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=20),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            # create the byte string encoded token using payload and SECRET key
            jwt_string = jwt.encode(
                payload,
                SECRET_KEY,
                algorithm='HS256'
            )
            return jwt_string

        except Exception as e:
            # return an error in string format if an exception occurs
            return str(e)

    @staticmethod
    def decode_token(token):
        """ Handles the decoding of a token from the Authorization header"""
        try:
            # Decode token with our secret key
            payload = jwt.decode(token, SECRET_KEY)
            return payload['sub']
        except jwt.ExpiredSignatureError:
            # token has expired
            return "Timed out. Please login to get a new token"
        except jwt.InvalidTokenError:
            return "Invalid token. Please register or login"


class Shoppinglist(db.Model):
    """Class represents Shoppinglist table"""
    __tablename__ = 'shoppinglists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(
    ), onupdate=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey(User.id))
    shoppingitems = db.relationship(
        'Shoppingitem', order_by='Shoppingitem.id', cascade='all, delete-orphan')

    def __init__(self, name, created_by):
        """" Initialize with name and creator"""
        self.name = name
        self.created_by = created_by

    def save(self):
        """Save a shopping list"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all(user_id):
        """Get all shopping lists belonging to user who created them"""
        return Shoppinglist.query.filter_by(created_by=user_id)

    def delete(self):
        """Delete a shopping list"""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Shoppinglist: {}>".format(self.name)


class Shoppingitem(db.Model):
    """Class represents shoppingitems table"""
    __tablename__ = "shoppingitems"

    # Define columns for users table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(
    ), onupdate=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey(User.id))
    in_shoppinglist = db.Column(db.Integer, db.ForeignKey(Shoppinglist.id))

    def __init__(self, name, in_shoppinglist, created_by):
        """Initialize a shopping item with a name, shopping list and user"""
        self.name = name
        self.in_shoppinglist = in_shoppinglist
        self.created_by = created_by

    def save(self):
        """Add and save a shopping item"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all_items(slist_id, user_id):
        """Get all shopping items belonging to a shopping list and creator"""
        return Shoppingitem.query.filter_by(in_shoppinglist=slist_id, created_by=user_id)

    def delete(self):
        """Delete a shopping item"""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Shoppingitem: {}>".format(self.name)
