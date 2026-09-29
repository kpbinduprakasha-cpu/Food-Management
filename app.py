import os
from flask import Flask, render_template
from config import Config
from extensions import db, migrate, login_manager, bcrypt

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # Import models
    from models import User, SenderProfile, ReceiverProfile
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.sender import sender_bp
    from routes.receiver import receiver_bp
    from routes.admin import admin_bp
    from routes.food import food_bp
    from routes.tracking import tracking_bp
    from routes.profile import profile_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(sender_bp)
    app.register_blueprint(receiver_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(food_bp)
    app.register_blueprint(tracking_bp)
    app.register_blueprint(profile_bp)
    
    @app.route('/')
    def index():
        return render_template('base.html')
        
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        from flask import send_from_directory
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        
    # Create tables if not exists
    with app.app_context():
        db.create_all()
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
