from extensions import db
from models import Message, Conversation, Document, ConsentRequest, AuditLog
from sqlalchemy.orm import joinedload
from datetime import datetime


class ConversationRepository:
    @staticmethod
    def get_conversation(conversation_id):
        return Conversation.query.get(conversation_id)


    @staticmethod
    def get_messages(conversation_id, page=1, page_size=50):
        q = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at.desc())
        items = q.paginate(page=page, per_page=page_size, error_out=False)
        return items


    @staticmethod
    def add_message(conversation_id, sender_id, content=None, message_type='text', attachment=None, expires_at=None, ephemeral=False):
        msg = Message(conversation_id=conversation_id, sender_id=sender_id, content=content, message_type=message_type,
                  attachment=attachment, expires_at=expires_at, ephemeral=ephemeral)
        db.session.add(msg)
        db.session.commit()
        return msg


class DocumentRepository:
    @staticmethod
    def create_document(owner_id, filename, s3_key, mime_type=None, size=None, expires_at=None, single_use=False):
        doc = Document(owner_id=owner_id, filename=filename, s3_key=s3_key, mime_type=mime_type, size=size, expires_at=expires_at, single_use=single_use)
        db.session.add(doc)
        db.session.commit()
        return doc


class ConsentRepository:
    @staticmethod
    def request_consent(requester_id, owner_id, target_type, target_id):
        req = ConsentRequest(requester_id=requester_id, owner_id=owner_id, target_type=target_type, target_id=target_id)
        db.session.add(req)
        db.session.commit()
        return req


    @staticmethod
    def respond_consent(consent_id, owner_id, approve: bool):
        req = ConsentRequest.query.get(consent_id)
        if req is None or req.owner_id != owner_id:
            return None
        req.status = 'approved' if approve else 'denied'
        req.responded_at = datetime.utcnow()
        db.session.commit()
        return req


class AuditRepository:
    @staticmethod
    def log(actor_id, action, target_type=None, target_id=None, details=None):
        log = AuditLog(actor_id=actor_id, action=action, target_type=target_type, target_id=target_id, details=details)
        db.session.add(log)
        db.session.commit()
        return log