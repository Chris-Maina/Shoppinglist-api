""" models.py """

from app import db
from flask_bcrypt import Bcrypt

class User(db.Model):
    """Class represents Users table"""
    __tablename__ = 'users'

    # Define columns for users table
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    shoppinglists = db.relationship('Shoppinglist', order_by='Shoppinglist.id', cascade="all, delete-orphan")

    def __init__(self, email, password):
        """Initialize the user with an email and password."""
        self.email = email
        self.password = Bcrypt.generate_password_hash(password).decode()
    
    def password_is_valid(self, password):
        """ Check password against it's hash to validate user's password"""
        return Bcrypt().check_password_hash(self.password, password)

    def save(self):
        """ Save a user to a db"""
        db.session.add(self)
        db.session.commit()

class Shoppinglist(db.Model):
    """Class represents Shoppinglist table"""
    __tablename__ = 'shoppinglists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(
    ), onupdate=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey(User.id))

    def __init__(self, name):
        """" Initialize with name"""
        self.name = name

    def save(self):
        """Save a shopping list"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        """Get all shopping lists"""
        return Shoppinglist.query.all()

    def delete(self):
        """Delete a shopping list"""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Shoppinglist: {}>".format(self.name)
