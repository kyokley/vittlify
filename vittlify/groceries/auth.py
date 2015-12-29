from rest_framework.authentication import SessionAuthentication
from config.settings import ALEXA_PASS

class UnsafeSessionAuthentication(SessionAuthentication):
    def authenticate(self, request):
        if request.data.get('pass') != ALEXA_PASS:
            raise Exception('Auth failed')

        http_request = request._request
        user = getattr(http_request, 'user', None)

        if not user or not user.is_active:
           return None

        return (user, None)
