from flask import Flask
from extensions import db
from routes.routing import routing_bp

"""
This file sets up the Flask application and SQLAlchemy database connection.
"""
# Create the Flask application
app = Flask(__name__)

# Configure the database 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Unsalted2025@localhost:5432/pollution_routing'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# Register the routing blueprint
app.register_blueprint(routing_bp)

