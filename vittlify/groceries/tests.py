from django.test import TestCase

from groceries.views import signin
import mock

class test_signin(TestCase):
    def setUp(self):
        self.request = mock.MagicMock()
        self.request.method = 'POST'

    @mock.patch('groceries.views.SignInForm')
    def test_case_insensitive_username(self, mock_SignInForm):
        pass
