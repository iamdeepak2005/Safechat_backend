from extensions import db
from datetime import datetime

class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.BigInteger, primary_key=True)
    owner_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=True)
    file_hash = db.Column(db.String(64), nullable=True)
    capsule_id = db.Column(db.BigInteger, db.ForeignKey('capsules.id'), nullable=True)
    encrypted_blob = db.Column(db.LargeBinary(length=(2**32 - 1)), nullable=False)
    view_once = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owner = db.relationship("User", backref="files")
    capsule = db.relationship("Capsule", back_populates="files")
