from flask import Blueprint, current_app, request, jsonify
from extensions import db
from models import Message, Conversation, User, Document
from repositories import ConversationRepository, AuditRepository
from schemas import MessageSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta


bp = Blueprint('messages', __name__)
message_schema = MessageSchema()


@bp.route('/conversation/<int:conversation_id>', methods=['GET'])
@jwt_required()
def get_messages(conversation_id):
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 50))
    paginated = ConversationRepository.get_messages(conversation_id, page=page, page_size=page_size)


    items = [message_schema.dump(m) for m in paginated.items]
    return jsonify({
        'items': items,
        'page': paginated.page,
        'pages': paginated.pages,
        'total': paginated.total
        })
@bp.route('/conversation/<int:conversation_id>', methods=['POST'])
@jwt_required()
def post_message(conversation_id):
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    content = data.get('content')
    message_type = data.get('message_type', 'text')
    ephemeral = data.get('ephemeral', False)
    ttl = data.get('ttl_seconds')
    expires_at = None
    if ephemeral:
        ttl = ttl or current_app.config.get('DEFAULT_MESSAGE_TTL_SECONDS')
        expires_at = datetime.utcnow() + timedelta(seconds=int(ttl))


# if attachment: assume frontend will upload to S3 and provide document_id
    attachment_id = data.get('attachment_id')


    msg = ConversationRepository.add_message(conversation_id=conversation_id, sender_id=user_id,
                                             content=content, message_type=message_type,
                                             attachment=attachment_id, expires_at=expires_at, ephemeral=ephemeral)


    AuditRepository.log(actor_id=user_id, action='message_sent', target_type='conversation', target_id=conversation_id, details={'message_id': msg.id})
    return jsonify(message_schema.dump(msg)), 201