from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.tracking import TrackingSession
from models.request import FoodRequest

tracking_bp = Blueprint('tracking', __name__, url_prefix='/tracking')

@tracking_bp.route('/start/<int:request_id>')
@login_required
def start_tracking(request_id):
    if current_user.role != 'receiver':
        return "Unauthorized", 403
        
    req = FoodRequest.query.get_or_404(request_id)
    if req.receiver_id != current_user.id or req.status != 'Accepted':
        flash('Invalid request to track.', 'danger')
        return redirect(url_for('receiver.my_requests'))
        
    # Create tracking session if not exists
    session = TrackingSession.query.filter_by(request_id=req.id).first()
    if not session:
        session = TrackingSession(
            request_id=req.id,
            dest_lat=req.donation.latitude,
            dest_lng=req.donation.longitude
        )
        req.status = 'In Transit'
        req.donation.status = 'In Transit'
        db.session.add(session)
        db.session.commit()
        
    return render_template('tracking/receiver_view.html', session=session, req=req)

@tracking_bp.route('/update_location', methods=['POST'])
@login_required
def update_location():
    if current_user.role != 'receiver':
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.json
    session_id = data.get('session_id')
    lat = data.get('lat')
    lng = data.get('lng')
    
    session = TrackingSession.query.get(session_id)
    if session and session.request.receiver_id == current_user.id:
        session.current_lat = lat
        session.current_lng = lng
        db.session.commit()
        return jsonify({'status': 'success'})
        
    return jsonify({'error': 'Invalid session'}), 400

@tracking_bp.route('/view/<int:request_id>')
@login_required
def view_tracking(request_id):
    if current_user.role != 'sender':
        return "Unauthorized", 403
        
    req = FoodRequest.query.get_or_404(request_id)
    if req.donation.sender_id != current_user.id:
        return "Unauthorized", 403
        
    session = TrackingSession.query.filter_by(request_id=req.id).first()
    if not session:
        flash('Tracking has not started yet.', 'info')
        return redirect(url_for('sender.requests'))
        
    return render_template('tracking/sender_view.html', session=session, req=req)

@tracking_bp.route('/api/location/<int:session_id>')
@login_required
def get_location(session_id):
    session = TrackingSession.query.get_or_404(session_id)
    # Basic auth check
    if current_user.role == 'sender' and session.request.donation.sender_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    return jsonify({
        'lat': session.current_lat,
        'lng': session.current_lng,
        'status': session.status
    })

@tracking_bp.route('/complete/<int:session_id>', methods=['POST'])
@login_required
def complete_collection(session_id):
    session = TrackingSession.query.get_or_404(session_id)
    # Both sender and receiver can complete it
    if current_user.id not in [session.request.receiver_id, session.request.donation.sender_id]:
        return "Unauthorized", 403
        
    session.status = 'Completed'
    session.request.status = 'Completed'
    session.request.donation.status = 'Completed'
    
    db.session.commit()
    flash('Food collection marked as completed. Thank you!', 'success')
    
    if current_user.role == 'sender':
        return redirect(url_for('sender.dashboard'))
    else:
        return redirect(url_for('receiver.dashboard'))
