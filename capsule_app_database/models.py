from datetime import datetime
from extensions import db
from sqlalchemy import Index
from sqlalchemy.orm import relationship


conversation_participants = db.Table(
    'conversation_participants',
    db.Column('conversation_id', db.Integer, db.ForeignKey('conversation.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
    )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    sent_messages = relationship('Message', back_populates='sender', lazy='dynamic')


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=True)
    is_group = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    participants = relationship('User', secondary=conversation_participants, backref='conversations')
    messages = relationship('Message', back_populates='conversation', lazy='dynamic')


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), index=True, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=True)
    message_type = db.Column(db.String(40), default='text') # text/image/document
    attachment_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    expires_at = db.Column(db.DateTime, nullable=True, index=True)
    ephemeral = db.Column(db.Boolean, default=False)


    conversation = relationship('Conversation', back_populates='messages')
    sender = relationship('User', back_populates='sent_messages')
    attachment = relationship('Document')
    def is_expired(self):
        if self.expires_at is None:
            return False
        return datetime.utcnow() >= self.expires_at


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(512), nullable=False)
    s3_key = db.Column(db.String(1024), nullable=False, unique=True)
    mime_type = db.Column(db.String(120), nullable=True)
    size = db.Column(db.BigInteger, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    single_use = db.Column(db.Boolean, default=False)


    owner = relationship('User')


class ConsentRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    target_type = db.Column(db.String(40), nullable=False) # 'message' or 'document'
    target_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending/approved/denied
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime, nullable=True)


    requester = relationship('User', foreign_keys=[requester_id])
    owner = relationship('User', foreign_keys=[owner_id])


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(120), nullable=False)
    target_type = db.Column(db.String(40), nullable=True)
    target_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.JSON, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)


    actor = relationship('User')


# Useful indexes
Index('ix_message_conv_created', Message.conversation_id, Message.created_at)