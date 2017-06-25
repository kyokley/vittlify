from rest_framework.authentication import SessionAuthentication
from config.settings import ALEXA_PASS
from groceries.models import SshKey, Shopper

class UnsafeSessionAuthentication(SessionAuthentication):
    def authenticate(self, request):
        if request.data.get('pass') != ALEXA_PASS:
            raise Exception('Auth failed')

        http_request = request._request
        user = getattr(http_request, 'user', None)

        if not user or not user.is_active:
           return None

        return (user, None)

class LocalSessionAuthentication(SessionAuthentication):
    def authenticate(self, request):
        #if 'localhost' not in request.META['HTTP_HOST']:
            #raise Exception('External request is being made for internal-only service')

        http_request = request._request
        user = getattr(http_request, 'user', None)

        if not user or not user.is_active:
           return None

        return (user, None)

class SshSessionAuthentication(SessionAuthentication):
    def authenticate(self, request):
        data = request.data
        message = data['message']
        signature = data['signature']

        shopper_id = request.data.get('shopper')
        shopper = Shopper.objects.get(pk=shopper_id)

        for sshkey in shopper.sshkey_set.all():
            if sshkey.verify(message, signature):
                return (request.user, None)

        return None
