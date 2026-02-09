# usabel only for first time to create the db

from flask import Flask
from models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)

with app.app_context():
    db.create_all()
    print("Database created successfully!")