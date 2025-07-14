from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    priority = db.Column(db.String(20), default='medium', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        """Convertit l'objet Task en dictionnaire pour JSON"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'priority': self.priority,
            'created_at': (self.created_at.isoformat()
                          if self.created_at else None),
            'updated_at': (self.updated_at.isoformat()
                          if self.updated_at else None),
            'due_date': (self.due_date.isoformat()
                        if self.due_date else None)
        }

    def __repr__(self):
        return f'<Task {self.id}: {self.title}>'


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': (self.created_at.isoformat()
                          if self.created_at else None)
        }

    def __repr__(self):
        return f'<User {self.username}>'