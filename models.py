from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default=lambda: f"Batch {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    sender_email = db.Column(db.String(120))
    sender_password = db.Column(db.String(120))
    subject = db.Column(db.String(200))
    body = db.Column(db.Text)
    host_url = db.Column(db.String(200))
    redirect_url = db.Column(db.String(500))
    targets = db.relationship('Target', backref='campaign', lazy=True)

class Target(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    tracking_id = db.Column(db.String(36), unique=True, nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    status = db.Column(db.String(20), default='sent')
    events = db.relationship('Event', backref='target', lazy=True)
    form_data = db.relationship('FormData', backref='target', lazy=True)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(200))
    target_id = db.Column(db.Integer, db.ForeignKey('target.id'), nullable=False)

class FormData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.JSON, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    target_id = db.Column(db.Integer, db.ForeignKey('target.id'), nullable=False)
