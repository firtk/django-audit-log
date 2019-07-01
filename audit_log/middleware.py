from django.db.models import signals
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import curry

from audit_log import registration, settings
from audit_log.models import fields
from audit_log.models.managers import AuditLogManager


def _disable_audit_log_managers(instance):
    for attr in dir(instance):
        try:
            if isinstance(getattr(instance, attr), AuditLogManager):
                getattr(instance, attr).disable_tracking()
        except AttributeError:
            pass


def _enable_audit_log_managers(instance):
    for attr in dir(instance):
        try:
            if isinstance(getattr(instance, attr), AuditLogManager):
                getattr(instance, attr).enable_tracking()
        except AttributeError:
            pass


def _get_user_from_request(request):
    if hasattr(request, 'user') and request.user.is_authenticated:
        return request.user
    if getattr(request, '_drf_audit_user', None) and request._drf_audit_user.is_authenticated:
        return request._drf_audit_user
    return None


class UserLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if settings.DISABLE_AUDIT_LOG:
            return
        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            user = _get_user_from_request(request)
            session = request.session.session_key
            update_pre_save_info = curry(self._update_pre_save_info, user, session)
            signals.pre_save.connect(update_pre_save_info,  dispatch_uid = (self.__class__, request,), weak = False)

    def process_response(self, request, response):
        if settings.DISABLE_AUDIT_LOG:
            return
        signals.pre_save.disconnect(dispatch_uid =  (self.__class__, request,))
        return response

    def process_exception(self, request, exception):
        if settings.DISABLE_AUDIT_LOG:
            return None
        signals.pre_save.disconnect(dispatch_uid =  (self.__class__, request,))
        return None

    def _update_pre_save_info(self, user, session, sender, instance, **kwargs):
        # creating fields
        is_adding = instance._state.adding  # Access to django internal stuff, may change in next version
        if not instance.pk or is_adding:  # instance.pk may be set manually, check additionally the `is_adding`
            registry = registration.FieldRegistry(fields.CreatingUserField)
            if sender in registry:
                for field in registry.get_fields(sender):
                    if not getattr(instance, field.name, None):
                        setattr(instance, field.name, user)

            registry = registration.FieldRegistry(fields.CreatingSessionKeyField)
            if sender in registry:
                for field in registry.get_fields(sender):
                    if not getattr(instance, field.name, None):
                        setattr(instance, field.name, session)

        # modifying fields
        registry = registration.FieldRegistry(fields.LastUserField)
        if sender in registry:
            for field in registry.get_fields(sender):
                if not fields.is_field_changed(instance, field.name):
                    setattr(instance, field.name, user)

        registry = registration.FieldRegistry(fields.LastSessionKeyField)
        if sender in registry:
            for field in registry.get_fields(sender):
                setattr(instance, field.name, session)


class JWTAuthMiddleware(MiddlewareMixin):
    """
    Convenience middleware for users of django-rest-framework-jwt.
    Fixes issue https://github.com/GetBlimp/django-rest-framework-jwt/issues/45
    """


    def get_user_jwt(self, request):
        from rest_framework.request import Request
        from rest_framework.exceptions import AuthenticationFailed
        from django.contrib.auth.middleware import get_user
        from rest_framework_jwt.authentication import JSONWebTokenAuthentication

        user = get_user(request)
        if user.is_authenticated:
            return user
        try:
            user_jwt = JSONWebTokenAuthentication().authenticate(Request(request))
            if user_jwt is not None:
                return user_jwt[0]
        except AuthenticationFailed:
            pass
        return user

    def process_request(self, request):
        from django.utils.functional import SimpleLazyObject
        assert hasattr(request, 'session'),\
        """The Django authentication middleware requires session middleware to be installed.
         Edit your MIDDLEWARE setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."""

        request.user = SimpleLazyObject(lambda: self.get_user_jwt(request))


class AuditJWTAuthMiddleware(MiddlewareMixin):
    """
    Different implementation of JWTAuthMiddleware: it doesn't change the existing
    authentication flow (i.e. it doesn't change request object).

    It allows to specify custom authenticator for JWT as well.
    """

    def get_user_jwt(self, request):
        from django.contrib.auth.middleware import get_user
        from rest_framework.request import Request
        from rest_framework.exceptions import APIException
        from rest_framework.settings import import_from_string

        user = get_user(request)
        if user.is_authenticated:
            return user
        jwt_authenticator = import_from_string(
            settings.AUDIT_LOG_JWT_AUTHENTICATOR,
            'AUDIT_LOG_JWT_AUTHENTICATOR',
        )
        user_auth_tuple = None
        try:
            user_auth_tuple = jwt_authenticator().authenticate(Request(request))
        except APIException:
            pass
        if user_auth_tuple is not None:
            user = user_auth_tuple[0]
        return user

    def process_request(self, request):
        from django.utils.functional import SimpleLazyObject
        assert hasattr(request, 'session'),\
        """The Django authentication middleware requires session middleware to be installed.
         Edit your MIDDLEWARE setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."""

        request._drf_audit_user = SimpleLazyObject(lambda: self.get_user_jwt(request))
