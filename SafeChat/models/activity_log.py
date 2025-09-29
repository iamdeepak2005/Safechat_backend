from datetime import datetime
from extensions import db

class FileActivityLog(db.Model):
    __tablename__ = 'file_activity_log'

    id = db.Column(db.BigInteger, primary_key=True)
    file_id = db.Column(db.BigInteger, db.ForeignKey('files.id'), nullable=False)
    actor_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    action_type = db.Column(db.Enum(
        'view', 'download', 'forward', 'attempt_forward',
        'permission_grant', 'permission_revoke'
    ), nullable=False)
    target_user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text)

    file = db.relationship("File")
