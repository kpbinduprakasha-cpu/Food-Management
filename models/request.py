from extensions import db
from datetime import datetime

class FoodRequest(db.Model):
    __tablename__ = 'food_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(db.Integer, db.ForeignKey('food_donations.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    status = db.Column(db.String(20), default='Requested') # Requested, Accepted, Rejected, In Transit, Arrived, Collected, Completed
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    donation = db.relationship('FoodDonation', backref='requests')
    receiver = db.relationship('User', backref='requests_made')
