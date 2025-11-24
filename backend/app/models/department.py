from app import db
from datetime import datetime
from enum import Enum

class DepartmentStatus(Enum):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)
    manager_id = db.Column(db.String(20), db.ForeignKey('users.id'))
    location = db.Column(db.String(100))
    status = db.Column(db.Enum(DepartmentStatus), default=DepartmentStatus.ACTIVE, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = db.relationship('User', backref='department_obj', lazy='dynamic', foreign_keys='User.department')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'manager_id': self.manager_id,
            'location': self.location,
            'status': self.status.value
        }
