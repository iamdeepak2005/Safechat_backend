from extensions import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.BigInteger, primary_key=True)  # can also keep Integer if you want
    file_id = db.Column(db.BigInteger, db.ForeignKey("files.id"), nullable=False)
    from_user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    to_user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending, approved, denied
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    file = db.relationship("File", backref="notifications")
    from_user = db.relationship("User", foreign_keys=[from_user_id])
    to_user = db.relationship("User", foreign_keys=[to_user_id])
