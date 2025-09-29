from flask import Blueprint, request, jsonify, send_file
from extensions import db
from models.user import User
from models.file import File
from models.notifications import Notification
from models.capsule import Capsule
from services.security import encrypt_file, decrypt_file, notify_owner
import io

files_bp = Blueprint('files', __name__)

# -------------------------------
# Upload / Capsule File
# -------------------------------
@files_bp.route('/upload', methods=['POST'])
def upload_file():
    user_id = request.form.get('user_id')
    file = request.files.get('file')
    view_once = request.form.get('view_once', 'false').lower() == 'true'
    capsule_flag = request.form.get('capsule_id')  # can be 'true', 'false', or an ID

    if not user_id or not file:
        return jsonify({"error": "user_id and file required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    capsule = None
    # 🧠 CASE 1: User wants a new capsule (capsule_id == 'true')
    if capsule_flag and capsule_flag.lower() == "true":
        capsule = Capsule(
            name=f"Capsule_{user.username}_{file.filename}",
            description=f"Auto-created capsule for {file.filename}",
            created_by=user.id
        )
        db.session.add(capsule)
        db.session.flush()  # ensures capsule.id is available before inserting file

    # 🧠 CASE 2: User passed an existing capsule ID
    elif capsule_flag and capsule_flag.isdigit():
        capsule = Capsule.query.get(int(capsule_flag))
        if not capsule:
            return jsonify({"error": "Invalid capsule_id"}), 404

    # 🧠 CASE 3: capsule_flag is "false" or empty → no capsule linked
    else:
        capsule = None

    # 🔐 Encrypt file and store it as blob
    encrypted_data = encrypt_file(file.read())

    new_file = File(
        filename=file.filename,
        owner_id=user.id,
        encrypted_blob=encrypted_data,
        view_once=view_once,
        capsule_id=capsule.id if capsule else None
    )
    db.session.add(new_file)
    db.session.commit()

    return jsonify({
        "message": "File uploaded securely",
        "file_id": new_file.id,
        "capsule_id": capsule.id if capsule else None
    }), 201

# -------------------------------
# Share File (with owner approval workflow)
# -------------------------------
@files_bp.route('/share', methods=['POST'])
def share_file():
    file_id = request.json.get('file_id')
    from_user_id = request.json.get('from_user_id')
    to_user_id = request.json.get('to_user_id')

    file = File.query.get(file_id)
    from_user = User.query.get(from_user_id)
    to_user = User.query.get(to_user_id)

    if not file or not from_user or not to_user:
        return jsonify({"error": "Invalid file or user"}), 404

    # Only enforce approval if the file is part of a capsule and the sharer is not the owner
    if file.capsule_id and file.owner_id != from_user.id:
        # Check if there's already an approved notification for this user
        approved_notif = Notification.query.filter_by(
            file_id=file.id,
            from_user_id=from_user.id,
            to_user_id=file.owner_id,
            status='approve'
        ).first()

        if not approved_notif:
            # Create a pending notification for owner approval
            message = f"{from_user.username} wants to share your file '{file.filename}' with {to_user.username}"
            notif = Notification(
                file_id=file.id,
                from_user_id=from_user.id,
                to_user_id=file.owner_id,
                message=message,
                status="pending"
            )
            db.session.add(notif)
            db.session.commit()
            return jsonify({"message": "Owner approval required. Notification sent."})

    # If owner is sharing or already approved → share directly
    message = f"{from_user.username} shared your file '{file.filename}' with {to_user.username}"
    notify_owner(file.owner, message)
    return jsonify({"message": f"File shared with {to_user.username}"})

# -------------------------------
# Access File
# -------------------------------
@files_bp.route('/access/<int:file_id>/<int:user_id>', methods=['GET'])
def access_file(file_id, user_id):
    file = File.query.get(file_id)
    user = User.query.get(user_id)

    if not file or not user:
        return jsonify({"error": "File or user not found"}), 404

    # Check permission: only owner or explicitly shared
    if user.id != file.owner_id:
        return jsonify({"error": "Access denied"}), 403

    decrypted_data = decrypt_file(file.encrypted_blob)
    file_stream = io.BytesIO(decrypted_data)

    if file.view_once:
        db.session.delete(file)
        db.session.commit()

    return send_file(file_stream, download_name=file.filename, as_attachment=True)


# -------------------------------
# List Files Owned by User
# -------------------------------
@files_bp.route('/list/<int:user_id>', methods=['GET'])
def list_files(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    files = [
        {"file_id": f.id, "filename": f.filename, "view_once": f.view_once}
        for f in user.files
    ]
    return jsonify({"files": files})


# -------------------------------
# List Notifications for a User
# -------------------------------
@files_bp.route('/notifications/<int:user_id>', methods=['GET'])
def get_notifications(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    notifs = Notification.query.filter_by(to_user_id=user_id).all()
    result = [
        {
            "id": n.id,
            "file": n.file.filename,
            "from_user": n.from_user.username,
            "message": n.message,
            "status": n.status,
            "created_at": n.created_at
        }
        for n in notifs
    ]
    return jsonify({"notifications": result})


# -------------------------------
# Approve / Deny Notification
# -------------------------------
@files_bp.route('/notifications/<int:notif_id>/action', methods=['POST'])
def handle_notification(notif_id):
    action = request.json.get("action")  # approve or deny
    notif = Notification.query.get(notif_id)
    if not notif:
        return jsonify({"error": "Notification not found"}), 404

    if action not in ["approve", "deny"]:
        return jsonify({"error": "Invalid action"}), 400

    notif.status = action
    db.session.commit()

    if action == "approve":
        notify_owner(notif.from_user, f"Your share request for '{notif.file.filename}' was approved.")
    else:
        notify_owner(notif.from_user, f"Your share request for '{notif.file.filename}' was denied.")

    return jsonify({"message": f"Notification {action}d"})
