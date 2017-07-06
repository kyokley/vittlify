import json
import base64
from rest_framework.authentication import SessionAuthentication
from config.settings import ALEXA_PASS
from groceries.models import Shopper

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
        message = json.loads(data['message'])
        signature = data['signature']

        username = message.get('username')
        shopper = Shopper.get_by_username(username)

        for sshkey in shopper.sshkey_set.all():
            if sshkey.verify(data['message'].encode('utf-8'),
                             base64.b64decode(signature)):
                return (shopper.user, None)

        return None
