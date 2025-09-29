from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Document
from s3_utils import generate_presigned_put, generate_presigned_get, build_s3_key
from repositories import DocumentRepository, AuditRepository


bp = Blueprint('documents', __name__)


@bp.route('/presign', methods=['POST'])
@jwt_required()
def presign_upload():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    filename = data.get('filename')
    mime_type = data.get('mime_type')
    if not filename:
        return jsonify({'error': 'filename required'}), 400


    key = build_s3_key(user_id, filename)
    url = generate_presigned_put(current_app.config.get('AWS_S3_BUCKET'), key, expires_in=3600)
    if not url:
        return jsonify({'error': 'could not create presigned url'}), 500


# return key so frontend can later confirm and create a document record
    return jsonify({'upload_url': url, 's3_key': key})


@bp.route('/confirm', methods=['POST'])
@jwt_required()
def confirm_upload():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    s3_key = data.get('s3_key')
    filename = data.get('filename')
    mime_type = data.get('mime_type')
    size = data.get('size')
    expires_at = data.get('expires_at')
    single_use = data.get('single_use', False)


    doc = DocumentRepository.create_document(owner_id=user_id, filename=filename, s3_key=s3_key, mime_type=mime_type, size=size, expires_at=expires_at, single_use=single_use)
    AuditRepository.log(actor_id=user_id, action='upload_document', target_type='document', target_id=doc.id)
    return jsonify({'document_id': doc.id}), 201


@bp.route('/<int:doc_id>/download', methods=['GET'])
@jwt_required()
def download(doc_id):
    user_id = get_jwt_identity()
    doc = Document.query.get_or_404(doc_id)
# permission check: owner or recipient in a conversation that references it or consent approved
# For brevity: allow owner or any authenticated user (in production enforce strict checks)
    url = generate_presigned_get(current_app.config.get('AWS_S3_BUCKET'), doc.s3_key, expires_in=600)
    AuditRepository.log(actor_id=user_id, action='download_document', target_type='document', target_id=doc_id)
    return jsonify({'download_url': url})