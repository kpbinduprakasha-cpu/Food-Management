from extensions import db
from datetime import datetime

class FoodCategory(db.Model):
    __tablename__ = 'food_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

class FoodDonation(db.Model):
    __tablename__ = 'food_donations'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('food_categories.id'), nullable=False)
    
    food_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False) # kg, servings, packets
    people_served = db.Column(db.Integer)
    
    food_image = db.Column(db.String(255))
    preparation_time = db.Column(db.DateTime)
    available_from = db.Column(db.DateTime, default=datetime.utcnow)
    best_before = db.Column(db.DateTime, nullable=False)
    
    pickup_location = db.Column(db.String(255))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    special_instructions = db.Column(db.Text)
    
    status = db.Column(db.String(20), default='Available') # Available, Requested, Accepted, Completed, Expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sender = db.relationship('User', backref='donations_made')
    category = db.relationship('FoodCategory', backref='foods')
