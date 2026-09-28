from extensions import db
from datetime import datetime

class TrackingSession(db.Model):
    __tablename__ = 'tracking_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('food_requests.id'), nullable=False)
    
    status = db.Column(db.String(20), default='Started') # Started, In Transit, Arrived, Collected, Completed
    
    # Current receiver location
    current_lat = db.Column(db.Float)
    current_lng = db.Column(db.Float)
    
    # Destination location
    dest_lat = db.Column(db.Float)
    dest_lng = db.Column(db.Float)
    
    distance_remaining = db.Column(db.Float) # in km
    eta_minutes = db.Column(db.Integer)
    
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    request = db.relationship('FoodRequest', backref=db.backref('tracking', uselist=False))
