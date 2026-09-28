from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, bcrypt
from models.user import User, SenderProfile, ReceiverProfile

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            # Redirect to appropriate dashboard based on role
            if user.role == 'sender':
                return redirect(url_for('sender.dashboard'))
            elif user.role == 'receiver':
                return redirect(url_for('receiver.dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    account_type = request.args.get('type')
    if account_type not in ['sender', 'receiver']:
        return render_template('register_choice.html')
        
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        mobile = request.form.get('mobile')
        email = request.form.get('email')
        password = request.form.get('password')
        organization_name = request.form.get('organization_name')
        
        # Check if email or mobile exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(request.url)
        if User.query.filter_by(mobile=mobile).first():
            flash('Mobile number already registered.', 'danger')
            return redirect(request.url)
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(
            full_name=full_name,
            mobile=mobile,
            email=email,
            password_hash=hashed_password,
            role=account_type
        )
        db.session.add(user)
        db.session.flush() # To get user.id
        
        if account_type == 'sender':
            sender_type = request.form.get('sender_type')
            profile = SenderProfile(
                user_id=user.id,
                organization_name=organization_name,
                account_type=sender_type
            )
            db.session.add(profile)
        else:
            receiver_type = request.form.get('receiver_type')
            profile = ReceiverProfile(
                user_id=user.id,
                organization_name=organization_name,
                receiver_type=receiver_type
            )
            db.session.add(profile)
            
        db.session.commit()
        flash('Account created successfully! You can now login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html', account_type=account_type)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))
