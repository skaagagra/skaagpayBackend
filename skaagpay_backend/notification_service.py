import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)

# Initialize Firebase App
if not firebase_admin._apps:
    cred_path = os.path.join(settings.BASE_DIR, 'serviceAccountKey.json')
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        logger.warning(f"Firebase Service Account Key not found at {cred_path}")

def send_notification(token, title, body, data=None):
    """
    Sends a push notification to a specific FCM token.
    """
    if not token:
        return
    
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            token=token,
        )
        response = messaging.send(message)
        logger.info(f"Successfully sent message: {response}")
        return response
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return None

def send_to_user(user, title, body, data=None):
    """
    Sends a notification to a specific user if they have an FCM token.
    """
    if user.fcm_token:
        return send_notification(user.fcm_token, title, body, data)
    return None

def send_to_admins(title, body, data=None):
    """
    Sends a notification to all Admin users.
    """
    from authentication.models import User
    admins = User.objects.filter(is_admin=True).exclude(fcm_token__isnull=True).exclude(fcm_token__exact='')
    
    count = 0
    for admin in admins:
        if admin.fcm_token:
            send_notification(admin.fcm_token, title, body, data)
            count += 1
    return count
