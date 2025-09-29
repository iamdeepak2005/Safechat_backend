from datetime import datetime
from extensions import db

class FilePermission(db.Model):
    __tablename__ = 'file_permissions'

    id = db.Column(db.BigInteger, primary_key=True)
    file_id = db.Column(db.BigInteger, db.ForeignKey('files.id'), nullable=False)
    granted_to = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    can_view = db.Column(db.Boolean, default=True)
    can_forward = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    file = db.relationship("File", backref="permissions")
