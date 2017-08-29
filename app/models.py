""" models.py """

from app import db


class Shoppinglist(db.Model):
    """Class represents Shoppinglist table"""
    __tablename__ = 'shoppinglists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(
    ), onupdate=db.func.current_timestamp())

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
