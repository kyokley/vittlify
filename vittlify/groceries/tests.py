from django.test import TestCase
from django.contrib.auth.models import User

from groceries.views import signin
import mock

class TestSignIn(TestCase):
    def setUp(self):
        self.request = mock.MagicMock()
        self.request.method = 'POST'

        self.password = 'a_pass'
        self.new_username = 'some_user'

        self.form = mock.MagicMock()
        self.form.cleaned_data = {'username': self.new_username,
                                  'password': self.password}

        self.new_user = User()
        self.new_user.username = self.new_username
        self.new_user.set_password(self.password)
        self.new_user.save()

    @mock.patch('groceries.views.login')
    @mock.patch('groceries.views.authenticate')
    @mock.patch('groceries.views.SignInForm')
    def test_form_is_invalid(self,
                             mock_SignInForm,
                             mock_authenticate,
                             mock_login):
        self.form.is_valid.return_value = False
        mock_SignInForm.return_value = self.form

        signin(self.request)

        self.assertFalse(mock_authenticate.called)
        self.assertFalse(mock_login.called)

    @mock.patch('groceries.views.login')
    @mock.patch('groceries.views.authenticate')
    @mock.patch('groceries.views.SignInForm')
    def test_case_insensitive_username(self,
                                       mock_SignInForm,
                                       mock_authenticate,
                                       mock_login):
        self.form.is_valid.return_value = True
        self.form.cleaned_data = {'username': self.new_username.upper(),
                                  'password': self.password}

        mock_SignInForm.return_value = self.form

        signin(self.request)
        mock_authenticate.assert_called_once_with(username=self.new_username,
                                                  password=self.password)
        self.assertTrue(mock_login.called)

    @mock.patch('groceries.views.login')
    @mock.patch('groceries.views.authenticate')
    @mock.patch('groceries.views.SignInForm')
    def test_user_is_inactive(self,
                              mock_SignInForm,
                              mock_authenticate,
                              mock_login):
        authenticated_user = mock.MagicMock()
        authenticated_user.is_active = False

        mock_authenticate.return_value = authenticated_user

        self.form.is_valid.return_value = True
        self.form.cleaned_data = {'username': self.new_username.upper(),
                                  'password': self.password}

        mock_SignInForm.return_value = self.form

        self.assertRaisesMessage(Exception,
                                 'Invalid User',
                                 signin,
                                 self.request)
        mock_authenticate.assert_called_once_with(username=self.new_username,
                                                  password=self.password)
        self.assertFalse(mock_login.called)

    @mock.patch('groceries.views.login')
    @mock.patch('groceries.views.authenticate')
    @mock.patch('groceries.views.SignInForm')
    def test_user_does_not_exist(self,
                                 mock_SignInForm,
                                 mock_authenticate,
                                 mock_login):
        authenticated_user = mock.MagicMock()
        authenticated_user.is_active = False

        mock_authenticate.return_value = authenticated_user

        self.form.is_valid.return_value = True
        self.form.cleaned_data = {'username': 'some_test_user_that_does_not_exist',
                                  'password': self.password}

        mock_SignInForm.return_value = self.form

        self.assertRaisesMessage(Exception,
                                 'Invalid User',
                                 signin,
                                 self.request)
        self.assertFalse(mock_authenticate.called)
        self.assertFalse(mock_login.called)
