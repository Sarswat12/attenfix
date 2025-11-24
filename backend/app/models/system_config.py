from app import db
from datetime import datetime

class SystemConfig(db.Model):
    __tablename__ = 'system_config'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    config_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    config_value = db.Column(db.Text, nullable=False)
    data_type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    is_editable = db.Column(db.Boolean, default=True)
    category = db.Column(db.String(50), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'config_key': self.config_key,
            'config_value': self.config_value,
            'data_type': self.data_type,
            'description': self.description,
            'is_editable': self.is_editable,
            'category': self.category
        }

    def get_value(self):
        """Parse config value based on data_type"""
        if self.data_type == 'number':
            return float(self.config_value)
        elif self.data_type == 'boolean':
            return self.config_value.lower() in ('true', '1', 'yes')
        elif self.data_type == 'json':
            import json
            return json.loads(self.config_value)
        else:
            return self.config_value
