from extensions import db
from datetime import datetime

class Capsule(db.Model):
    __tablename__ = 'capsules'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    creator = db.relationship('User', backref='capsules', lazy=True)
    files = db.relationship('File', back_populates='capsule', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Capsule {self.id} - {self.name}>"
