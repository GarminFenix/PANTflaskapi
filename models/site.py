"""
Defines th site model.
Author: Ross Cochrane
"""

from extensions import db
from geoalchemy2 import Geometry



class Site(db.Model):
    """
     A class representing a site in the database.
     """
    __tablename__ = 'sites'  # Match the actual table name

    system_code_number = db.Column(db.String, primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location = db.Column(Geometry('POINT', srid=4326))
