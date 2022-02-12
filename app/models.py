from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=False)

    # Foreign Keys


    # Methods to access relationships
    sessions = db.relationship('Session', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

bridge_session_skill = db.Table('bridge_session_skill',
    db.Column('session_id', db.Integer, db.ForeignKey('session.id'),
        primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id'),
        primary_key=True)
)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    level = db.Column(db.String(16), index=True, nullable=False)
    explanation = db.Column(db.Text, index=True, nullable=True)

    created = db.Column(db.DateTime, index=True, default=datetime.utcnow,
        nullable=False)
    edited = db.Column(db.DateTime, index=True, default=datetime.utcnow,
        nullable=False)
    starttime = db.Column(db.DateTime, index=True, nullable=True)
    endtime = db.Column(db.DateTime, index=True, nullable=True)

    private = db.Column(db.Boolean, default=False, nullable=False)

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Methods to access relationships
    skills = db.relationship('Skill', secondary=bridge_session_skill,
        lazy="dynamic", backref=db.backref('sessions', lazy=True))

    def __repr__(self):
        return '<Session {}>'.format(self.name)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, nullable=False)
    explanation = db.Column(db.Text, index=True, nullable=True)

    def __repr__(self):
        return '<Skill {}>'.format(self.name)
