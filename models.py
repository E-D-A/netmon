from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///provisioning.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'supersecret'
    db.init_app(app)
    return app

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='read-only')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Task(db.Model):
    id = db.Column(db.String, primary_key=True)
    user = db.Column(db.String)
    extension = db.Column(db.String)
    action = db.Column(db.String)
    source = db.Column(db.String(32))  # "Manual" or "Automatic"
    status = db.Column(db.String(32))  # Running, Success, Failed
    triggered_by = db.Column(db.String(100))  
    steps = db.Column(db.Text)          # JSON serialized steps
    created = db.Column(db.Float)       # timestamp
    last_updated = db.Column(db.Float)  # timestamp
