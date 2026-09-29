from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.user import User, SenderProfile, ReceiverProfile
import os
from werkzeug.utils import secure_filename
from flask import current_app

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/view/<int:user_id>')
def view(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('Admin profiles are private.', 'warning')
        return redirect(request.referrer or url_for('index'))
    return render_template('profile/view.html', user=user)

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if current_user.role == 'admin':
        flash('Admin settings not implemented yet.', 'info')
        return redirect(url_for('admin.dashboard'))
        
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name')
        current_user.mobile = request.form.get('mobile')
        
        # Handle profile image upload
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '':
                filename = secure_filename(f"{current_user.id}_{file.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles', filename)
                file.save(filepath)
                
                if current_user.role == 'sender':
                    current_user.sender_profile.profile_image = filename
                else:
                    current_user.receiver_profile.profile_image = filename
        
        if current_user.role == 'sender':
            current_user.sender_profile.organization_name = request.form.get('organization_name')
            current_user.sender_profile.account_type = request.form.get('account_type')
        elif current_user.role == 'receiver':
            current_user.receiver_profile.organization_name = request.form.get('organization_name')
            current_user.receiver_profile.receiver_type = request.form.get('receiver_type')
            
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        
        if current_user.role == 'sender':
            return redirect(url_for('sender.dashboard'))
        else:
            return redirect(url_for('receiver.dashboard'))
            
    return render_template('profile/edit.html')

@profile_bp.route('/history')
@login_required
def history():
    from models.food import FoodDonation
    from models.request import FoodRequest
    
    if current_user.role == 'sender':
        # Show all donations created by this sender
        donations = FoodDonation.query.filter_by(sender_id=current_user.id).order_by(FoodDonation.created_at.desc()).all()
        return render_template('profile/history_sender.html', donations=donations)
        
    elif current_user.role == 'receiver':
        # Show all requests made by this receiver
        requests = FoodRequest.query.filter_by(receiver_id=current_user.id).order_by(FoodRequest.created_at.desc()).all()
        return render_template('profile/history_receiver.html', requests=requests)
        
    return redirect(url_for('index'))
