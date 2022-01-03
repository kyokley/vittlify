from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User

from groceries.views import signin
from groceries.forms import ImportFileForm
from groceries.models import (ShoppingList,
                              Shopper,
                              Item,
                              )

from rest_framework import status
from rest_framework.test import APITestCase
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

class TestImportFile(TestCase):
    def setUp(self):
        self.form = ImportFileForm()
        self.shopping_list = mock.create_autospec(ShoppingList)
        self.form.cleaned_data = {'import_file': ('first',
                                                  'second',
                                                  'third',
                                                  'fourth'),
                                  'shopping_list': self.shopping_list}

    @mock.patch('groceries.forms.Item')
    def test_generate_items_from_file(self, mock_item):
        self.form.generate_items_from_file()

        mock_item.new.assert_any_call('first', self.shopping_list)
        mock_item.new.assert_any_call('second', self.shopping_list)
        mock_item.new.assert_any_call('third', self.shopping_list)
        mock_item.new.assert_any_call('fourth', self.shopping_list)
        self.assertEqual(mock_item.new.call_count, 4)

class TestShopperNew(TestCase):
    def setUp(self):
        self.test_user = User()
        self.test_user.username = 'test_user'
        self.test_user.email = 'test@user.com'
        self.test_user.save()

    def test_noUser_noUsername_noEmail(self):
        self.assertRaisesMessage(ValueError,
                                 'Either a user object or username and email must be provided',
                                 Shopper.new)

    def test_noUser_username_noEmail(self):
        self.assertRaisesMessage(ValueError,
                                 'Either a user object or username and email must be provided',
                                 Shopper.new,
                                 username='some_user')

    def test_noUser_noUsername_email(self):
        self.assertRaisesMessage(ValueError,
                                 'Either a user object or username and email must be provided',
                                 Shopper.new,
                                 email='test@user.com')

    def test_noUser_username_email(self):
        actual = Shopper.new(username='some_user',
                             email='test@user.com',
                             )
        self.assertEqual(actual.username, 'some_user')
        self.assertEqual(actual.email, 'test@user.com')
        self.assertEqual(actual.email_frequency, Shopper.WEEKLY)

    def test_user_noUsername_noEmail(self):
        actual = Shopper.new(user=self.test_user)
        self.assertEqual(actual.username, 'test_user')
        self.assertEqual(actual.email, 'test@user.com')
        self.assertEqual(actual.email_frequency, Shopper.WEEKLY)

class TestShoppingListItemsView(APITestCase):
    def setUp(self):
        self.test_shopper = Shopper.new(username='test_user',
                                        password='password',
                                        email='test@user.com')
        self.shopping_list = ShoppingList.new('test shopping list',
                                              self.test_shopper)
        self.item = Item.new('test item',
                             self.shopping_list)
        self.client.login(username='test_user', password='password')

    def test_(self):
        expected = {'done': False,
                    'name': u'test item',
                    'pk': 1,
                    'shopping_list_id': 1,
                    'category_id': None,
                    'comments': u'',
                    'guid': self.item.guid,
                    'category_name': None}
        response = self.client.get(reverse('groceries:shopping_list_items', args=[self.item.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(dict(response.data[0]), expected)
