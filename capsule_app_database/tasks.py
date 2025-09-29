from celery.schedules import crontab
from extensions import make_celery
from app import app as flask_app
from extensions import db
from models import Message, Document, AuditLog
from datetime import datetime
import boto3
from flask import current_app


celery = make_celery(flask_app)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60.0, sweep_expired.s(), name='sweep every minute')


@celery.task()
def sweep_expired():
    now = datetime.utcnow()
    expired_messages = Message.query.filter(Message.expires_at != None, Message.expires_at <= now).all()
    for m in expired_messages:
        AuditLog_entry = AuditLog(actor_id=m.sender_id, action='message_expired', target_type='message', target_id=m.id, details={'conversation_id': m.conversation_id})
        db.session.add(AuditLog_entry)
        db.session.delete(m)


    expired_docs = Document.query.filter(Document.expires_at != None, Document.expires_at <= now).all()
    s3 = boto3.client('s3', aws_access_key_id=flask_app.config.get('AWS_ACCESS_KEY_ID'), aws_secret_access_key=flask_app.config.get('AWS_SECRET_ACCESS_KEY'), region_name=flask_app.config.get('AWS_REGION'))
    bucket = flask_app.config.get('AWS_S3_BUCKET')
    for d in expired_docs:
        try:
            s3.delete_object(Bucket=bucket, Key=d.s3_key)
        except Exception as e:
            flask_app.logger.exception('failed deleting s3 key %s', d.s3_key)
            AuditLog_entry = AuditLog(actor_id=d.owner_id, action='document_expired_deleted', target_type='document', target_id=d.id)
            db.session.add(AuditLog_entry)
            db.session.delete(d)


    db.session.commit()


