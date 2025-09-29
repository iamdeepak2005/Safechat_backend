from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from repositories import ConsentRepository, AuditRepository


bp = Blueprint('consent', __name__)


@bp.route('/request', methods=['POST'])
@jwt_required()
def request_consent():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    owner_id = data.get('owner_id')
    target_type = data.get('target_type')
    target_id = data.get('target_id')
    if not all([owner_id, target_type, target_id]):
        return jsonify({'error': 'owner_id, target_type, target_id required'}), 400


    req = ConsentRepository.request_consent(requester_id=user_id, owner_id=owner_id, target_type=target_type, target_id=target_id)
    AuditRepository.log(actor_id=user_id, action='consent_requested', target_type=target_type, target_id=target_id)
    return jsonify({'consent_id': req.id}), 201


@bp.route('/<int:consent_id>/respond', methods=['POST'])
@jwt_required()
def respond_consent(consent_id):
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    approve = data.get('approve', False)
    req = ConsentRepository.respond_consent(consent_id, owner_id=user_id, approve=approve)
    if not req:
        return jsonify({'error': 'not found or not allowed'}), 404
    AuditRepository.log(actor_id=user_id, action='consent_responded', target_type=req.target_type, target_id=req.target_id, details={'approved': req.status == 'approved'})
    return jsonify({'status': req.status})