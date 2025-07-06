# create_db.py
from app import create_app, db
from app import models 

app = create_app()

with app.app_context():
    print(f"Connected to DB: {db.engine.url}")
    db.create_all()