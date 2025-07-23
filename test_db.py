from app import app, db
from models.site import Site

"""
Simple script to test database connection and query the Site model.
"""

with app.app_context():
    print("Querying the database for sites...")
    sites = Site.query.all()
    print(f"Found {len(sites)} site(s): {[site.system_code_number for site in sites]}")
    print("Query completed.")