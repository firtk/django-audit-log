from django.conf import settings as global_settings

DISABLE_AUDIT_LOG = getattr(global_settings, 'DISABLE_AUDIT_LOG', False)

AUDIT_LOG_JWT_AUTHENTICATOR = getattr(
    global_settings,
    'AUDIT_LOG_JWT_AUTHENTICATOR',
    'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
)
