from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import (ShoppingList,
                     Shopper,
                     Item,
                     )

class SignInForm(forms.Form):
    username = forms.CharField(max_length=100, label='Username')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')

    def clean(self):
        cleaned_data = super(SignInForm, self).clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if not username or not password:
            raise forms.ValidationError('Username and password fields are required.')

        user = User.objects.filter(username__iexact=username).first()
        user = authenticate(username=user.username, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError('Invalid username or password')

class ImportFileForm(forms.Form):
    import_file = forms.FileField()
    shopping_list = forms.ModelChoiceField(queryset=ShoppingList.objects.all())

    def __init__(self, *args, **kwargs):
        shopper_id = kwargs.pop('shopper_id', None)
        super(ImportFileForm, self).__init__(*args, **kwargs)
        if shopper_id:
            shopper = Shopper.objects.get(pk=shopper_id)
            self.fields['shopping_list'].queryset = ShoppingList.objects.filter(shoppinglistmember__shopper=shopper)

    def generate_items_from_file(self):
        for line in self.cleaned_data['import_file']:
            new_item = Item.new(line,
                                self.cleaned_data['shopping_list'])
            new_item.save()
