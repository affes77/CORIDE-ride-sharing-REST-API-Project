from db import db

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    rides = db.relationship('Ride', backref='driver', lazy=True)

class Ride(db.Model):
    ride_id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    start_location = db.Column(db.String(120), nullable=False)
    end_location = db.Column(db.String(120), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)