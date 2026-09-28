import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models.food import FoodDonation, FoodCategory
from datetime import datetime

food_bp = Blueprint('food', __name__, url_prefix='/food')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@food_bp.route('/donate', methods=['GET', 'POST'])
@login_required
def donate():
    if current_user.role != 'sender':
        flash('Only senders can donate food.', 'danger')
        return redirect(url_for('index'))
        
    categories = FoodCategory.query.all()
    
    if request.method == 'POST':
        food_name = request.form.get('food_name')
        category_id = request.form.get('category_id')
        description = request.form.get('description')
        quantity = request.form.get('quantity')
        unit = request.form.get('unit')
        people_served = request.form.get('people_served')
        
        # Handle datetime parsing
        best_before_str = request.form.get('best_before')
        best_before = datetime.strptime(best_before_str, '%Y-%m-%dT%H:%M') if best_before_str else None
        
        pickup_location = request.form.get('pickup_location')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        special_instructions = request.form.get('special_instructions')
        
        food = FoodDonation(
            sender_id=current_user.id,
            category_id=category_id,
            food_name=food_name,
            description=description,
            quantity=float(quantity),
            unit=unit,
            people_served=int(people_served) if people_served else None,
            best_before=best_before,
            pickup_location=pickup_location,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
            special_instructions=special_instructions
        )
        
        # Handle file upload
        if 'food_image' in request.files:
            file = request.files['food_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Create a unique filename
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'food', filename)
                file.save(file_path)
                food.food_image = filename
                
        db.session.add(food)
        db.session.commit()
        
        flash('Food donation published successfully!', 'success')
        return redirect(url_for('sender.dashboard'))
        
    return render_template('sender/donate.html', categories=categories)

@food_bp.route('/available')
@login_required
def available():
    if current_user.role != 'receiver':
        flash('Only receivers can view available food.', 'danger')
        return redirect(url_for('index'))
        
    donations = FoodDonation.query.filter(
        FoodDonation.status == 'Available',
        FoodDonation.best_before > datetime.utcnow()
    ).all()
    
    return render_template('receiver/available_food.html', donations=donations)

@food_bp.route('/<int:id>')
@login_required
def details(id):
    food = FoodDonation.query.get_or_404(id)
    return render_template('food/details.html', food=food)

@food_bp.route('/<int:id>/request', methods=['POST'])
@login_required
def request_food(id):
    if current_user.role != 'receiver':
        flash('Only receivers can request food.', 'danger')
        return redirect(url_for('index'))
        
    food = FoodDonation.query.get_or_404(id)
    if food.status != 'Available':
        flash('This food is no longer available.', 'danger')
        return redirect(url_for('food.available'))
        
    from models.request import FoodRequest
    
    # Check if already requested
    existing = FoodRequest.query.filter_by(donation_id=food.id, receiver_id=current_user.id).first()
    if existing:
        flash('You have already requested this food.', 'warning')
        return redirect(url_for('food.details', id=food.id))
        
    new_request = FoodRequest(
        donation_id=food.id,
        receiver_id=current_user.id
    )
    food.status = 'Requested'
    db.session.add(new_request)
    db.session.commit()
    
    flash('Food requested successfully! Waiting for sender approval.', 'success')
    return redirect(url_for('receiver.dashboard'))

