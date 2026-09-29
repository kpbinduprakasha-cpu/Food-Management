from flask import Blueprint, render_template
from flask_login import login_required, current_user

receiver_bp = Blueprint('receiver', __name__, url_prefix='/receiver')

@receiver_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'receiver':
        return "Unauthorized", 403
    from models.request import FoodRequest
    from models.food import FoodDonation
    
    # Active Requests
    my_requests = FoodRequest.query.filter_by(receiver_id=current_user.id, status='Requested').count()
    
    # Active Collections (Accepted or In Transit)
    active_collections = FoodRequest.query.filter(
        FoodRequest.receiver_id == current_user.id,
        FoodRequest.status.in_(['Accepted', 'In Transit'])
    ).count()
    
    # Let's fetch 3 latest available donations nearby
    recent_donations = FoodDonation.query.filter_by(status='Available').order_by(FoodDonation.created_at.desc()).limit(3).all()
    
    return render_template('receiver/dashboard.html', 
        my_requests=my_requests, 
        active_collections=active_collections,
        recent_donations=recent_donations
    )

@receiver_bp.route('/requests')
@login_required
def my_requests():
    if current_user.role != 'receiver':
        return "Unauthorized", 403
        
    from models.request import FoodRequest
    
    requests = FoodRequest.query.filter_by(receiver_id=current_user.id).order_by(FoodRequest.created_at.desc()).all()
    
    return render_template('receiver/requests.html', requests=requests)
