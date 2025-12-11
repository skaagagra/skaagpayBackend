import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
import os

# Initialize Firebase App
# In production, path to serviceAccountKey.json should be in settings or env
# For now, we will use a placeholder path or check if initialized
cred_path = os.path.join(settings.BASE_DIR, 'serviceAccountKey.json')

if not firebase_admin._apps:
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        print("WARNING: serviceAccountKey.json not found. Firebase not initialized.")

def send_user_notification(user, title, body):
    """
    Send notification to a specific user via their FCM token.
    """
    if not user.fcm_token:
        return
    
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=user.fcm_token,
        )
        response = messaging.send(message)
        print('Successfully sent message:', response)
    except Exception as e:
        print('Error sending message:', e)

def send_admin_notification(title, body):
    """
    Send notification to 'admin_alerts' topic.
    Admin app must subscribe to this topic.
    """
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            topic='admin_alerts',
        )
        response = messaging.send(message)
        print('Successfully sent admin message:', response)
    except Exception as e:
        print('Error sending admin message:', e)
