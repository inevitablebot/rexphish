from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Many-to-many: a campaign can rotate across multiple email templates
campaign_templates = db.Table('campaign_templates',
    db.Column('campaign_id', db.Integer, db.ForeignKey('campaign.id'), primary_key=True),
    db.Column('template_id', db.Integer, db.ForeignKey('email_template.id'), primary_key=True)
)

# Many-to-many: a campaign can rotate across multiple sending profiles
campaign_profiles = db.Table('campaign_profiles',
    db.Column('campaign_id', db.Integer, db.ForeignKey('campaign.id'), primary_key=True),
    db.Column('profile_id', db.Integer, db.ForeignKey('sending_profile.id'), primary_key=True)
)

class EmailTemplate(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(120), nullable=False)
    subject    = db.Column(db.String(200), nullable=False)
    body       = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class SendingProfile(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(120), nullable=False)
    email      = db.Column(db.String(120), nullable=False)
    password   = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Contact(db.Model):
    """Global, persistent contact list — survives across campaigns."""
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(120), nullable=False, default='')
    email      = db.Column(db.String(120), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Campaign(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(100), nullable=False, default=lambda: f"Batch {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    created_at      = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    sender_email    = db.Column(db.String(120))
    sender_password = db.Column(db.String(120))
    subject         = db.Column(db.String(200))
    body            = db.Column(db.Text)
    host_url        = db.Column(db.String(200))
    redirect_url    = db.Column(db.String(500))
    targets         = db.relationship('Target', backref='campaign', lazy=True)
    # Linked templates for rotation (optional — falls back to campaign subject/body if empty)
    templates       = db.relationship('EmailTemplate', secondary=campaign_templates, lazy='subquery')
    # Linked sending profiles for rotation (optional — falls back to campaign credentials if empty)
    profiles        = db.relationship('SendingProfile', secondary=campaign_profiles, lazy='subquery')

class Target(db.Model):
    id                 = db.Column(db.Integer, primary_key=True)
    email              = db.Column(db.String(120), nullable=False)
    name               = db.Column(db.String(120), nullable=True)   # target's display name for {{target}}
    tracking_id        = db.Column(db.String(36), unique=True, nullable=False)
    campaign_id        = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    status             = db.Column(db.String(20), default='Pending')
    sent_at            = db.Column(db.DateTime, nullable=True)       # timestamp when email was sent
    template_id        = db.Column(db.Integer, db.ForeignKey('email_template.id'), nullable=True)
    sending_profile_id = db.Column(db.Integer, db.ForeignKey('sending_profile.id'), nullable=True)
    events             = db.relationship('Event', backref='target', lazy=True)
    form_data          = db.relationship('FormData', backref='target', lazy=True)
    # Relationships for rotation info
    template           = db.relationship('EmailTemplate', lazy=True)
    sending_profile    = db.relationship('SendingProfile', lazy=True)

class Event(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    type       = db.Column(db.String(20), nullable=False)
    timestamp  = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(200))
    is_bot     = db.Column(db.Boolean, default=False)  # True if likely scanner/bot
    target_id  = db.Column(db.Integer, db.ForeignKey('target.id'), nullable=False)

class FormData(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    data      = db.Column(db.JSON, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))
    target_id = db.Column(db.Integer, db.ForeignKey('target.id'), nullable=False)
