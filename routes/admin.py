from flask import Blueprint, render_template
from flask_login import login_required, current_user

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return "Unauthorized", 403
        
    from models.user import User
    from models.food import FoodDonation
    from models.request import FoodRequest
    from models.tracking import TrackingSession
    
    total_users = User.query.count()
    total_senders = User.query.filter_by(role='sender').count()
    total_receivers = User.query.filter_by(role='receiver').count()
    active_donations = FoodDonation.query.filter_by(status='Available').count()
    
    return render_template('admin/dashboard.html', 
        total_users=total_users, 
        total_senders=total_senders,
        total_receivers=total_receivers,
        active_donations=active_donations
    )

@admin_bp.route('/users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        return "Unauthorized", 403
        
    from models.user import User
    users = User.query.filter(User.role != 'admin').all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>/verify', methods=['POST'])
@login_required
def verify_user(user_id):
    if current_user.role != 'admin':
        return "Unauthorized", 403
        
    from extensions import db
    from models.user import User
    
    user = User.query.get_or_404(user_id)
    # Toggle verification
    user.is_verified = not user.is_verified
    db.session.commit()
    
    status = "verified" if user.is_verified else "unverified"
    from flask import flash, redirect, url_for
    flash(f'User {user.full_name} is now {status}.', 'success')
    return redirect(url_for('admin.manage_users'))
