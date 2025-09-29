from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models import User, Message, Conversation, Document, ConsentRequest, AuditLog


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_relationships = True
        include_fk = True


class MessageSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Message
        load_instance = True
        include_relationships = True
        include_fk = True


class ConversationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Conversation
        load_instance = True
        include_relationships = True
        include_fk = True


class DocumentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Document
        load_instance = True
        include_relationships = True
        include_fk = True


class ConsentRequestSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ConsentRequest
        load_instance = True


class AuditLogSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = AuditLog
        load_instance = True