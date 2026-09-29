from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions import db

sender_bp = Blueprint('sender', __name__, url_prefix='/sender')

@sender_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'sender':
        return "Unauthorized", 403
    from models.food import FoodDonation
    from models.request import FoodRequest
    from sqlalchemy import func
    
    # Active Donations (Available or In Transit)
    active_donations = FoodDonation.query.filter(
        FoodDonation.sender_id == current_user.id,
        FoodDonation.status.in_(['Available', 'Accepted', 'In Transit'])
    ).count()
    
    # Pending Requests (Requests on this sender's food with 'Requested' status)
    pending_requests = db.session.query(FoodRequest).join(FoodDonation).filter(
        FoodDonation.sender_id == current_user.id,
        FoodRequest.status == 'Requested'
    ).count()
    
    # Completed Donations
    completed_donations = FoodDonation.query.filter_by(
        sender_id=current_user.id, 
        status='Completed'
    ).count()
    
    # People Served (sum of people_served for completed donations)
    people_served = db.session.query(func.sum(FoodDonation.people_served)).filter(
        FoodDonation.sender_id == current_user.id,
        FoodDonation.status == 'Completed'
    ).scalar() or 0
    
    return render_template('sender/dashboard.html',
        active_donations=active_donations,
        pending_requests=pending_requests,
        completed_donations=completed_donations,
        people_served=people_served
    )

@sender_bp.route('/requests')
@login_required
def requests():
    if current_user.role != 'sender':
        return "Unauthorized", 403
        
    from models.request import FoodRequest
    from models.food import FoodDonation
    
    # Get all requests for donations made by this sender
    user_requests = db.session.query(FoodRequest).join(FoodDonation).filter(
        FoodDonation.sender_id == current_user.id,
        FoodRequest.status.in_(['Requested', 'Accepted', 'In Transit'])
    ).all()
    
    return render_template('sender/requests.html', requests=user_requests)

@sender_bp.route('/request/<int:id>/<action>', methods=['POST'])
@login_required
def handle_request(id, action):
    if current_user.role != 'sender':
        return "Unauthorized", 403
        
    from models.request import FoodRequest
    
    req = FoodRequest.query.get_or_404(id)
    if req.donation.sender_id != current_user.id:
        return "Unauthorized", 403
        
    if action == 'accept':
        req.status = 'Accepted'
        req.donation.status = 'Accepted'
        
        # Reject other requests for this donation
        other_requests = FoodRequest.query.filter(
            FoodRequest.donation_id == req.donation_id,
            FoodRequest.id != req.id
        ).all()
        for other in other_requests:
            other.status = 'Rejected'
            
        flash('Request accepted! You can now track the receiver.', 'success')
    elif action == 'reject':
        req.status = 'Rejected'
        req.donation.status = 'Available'
        flash('Request rejected.', 'info')
        
    db.session.commit()
    return redirect(url_for('sender.requests'))
