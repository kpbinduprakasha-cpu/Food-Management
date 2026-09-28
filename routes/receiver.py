from flask import Blueprint, render_template
from flask_login import login_required, current_user

receiver_bp = Blueprint('receiver', __name__, url_prefix='/receiver')

@receiver_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'receiver':
        return "Unauthorized", 403
    return render_template('receiver/dashboard.html')

@receiver_bp.route('/requests')
@login_required
def my_requests():
    if current_user.role != 'receiver':
        return "Unauthorized", 403
        
    from models.request import FoodRequest
    
    requests = FoodRequest.query.filter_by(receiver_id=current_user.id).order_by(FoodRequest.created_at.desc()).all()
    
    return render_template('receiver/requests.html', requests=requests)
