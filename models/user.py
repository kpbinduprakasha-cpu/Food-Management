from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'sender', 'receiver', 'admin'
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sender_profile = db.relationship('SenderProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    receiver_profile = db.relationship('ReceiverProfile', backref='user', uselist=False, cascade="all, delete-orphan")

class SenderProfile(db.Model):
    __tablename__ = 'sender_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organization_name = db.Column(db.String(150))
    address = db.Column(db.Text)
    profile_image = db.Column(db.String(255))
    account_type = db.Column(db.String(50)) # Restaurant, Hotel, Individual, etc.
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    total_donations = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)

class ReceiverProfile(db.Model):
    __tablename__ = 'receiver_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organization_name = db.Column(db.String(150))
    address = db.Column(db.Text)
    profile_image = db.Column(db.String(255))
    receiver_type = db.Column(db.String(50)) # NGO, Shelter, Community Group, etc.
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    food_received = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)
