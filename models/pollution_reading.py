"""
Defines the pollution reading model.
"""

from extensions import db

class PollutionReading(db.Model):
    """
    Represents a dynamic pollution reading linked to a site.
    """
    __tablename__ = 'dynamic_readings'

    id = db.Column(db.Integer, primary_key=True)

    # Foreign key to Site.system_code_number
    system_code_number = db.Column(db.String, db.ForeignKey('sites.system_code_number'), nullable=False)

    co = db.Column(db.Float, nullable=True)
    no = db.Column(db.Float, nullable=True)
    no2 = db.Column(db.Float, nullable=True)
    temperature = db.Column(db.Float, nullable=True)
    rh = db.Column(db.Float, nullable=True)
    noise = db.Column(db.Float, nullable=True)
    battery = db.Column(db.Float, nullable=True)

    last_updated = db.Column(db.DateTime, nullable=False)

    # Relationship to Site
    site = db.relationship('Site', backref='dynamic_readings')
