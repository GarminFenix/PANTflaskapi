"""
Initializes the Flask application and configures the SQLAlchemy database connection.
"""

import os
from flask import Flask
from extensions import db
from routes.routing import routing_bp
from layers.site_location import sites_bp
from layers.heat_map import heatmap_bp
from dotenv import load_dotenv
   
"""
This file sets up the Flask application and SQLAlchemy database connection.
"""

load_dotenv()
# Create the Flask application
app = Flask(__name__)

# Configure the database 
import os

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# Blueprints
app.register_blueprint(routing_bp)
app.register_blueprint(sites_bp)
app.register_blueprint(heatmap_bp)

