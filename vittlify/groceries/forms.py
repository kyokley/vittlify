from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

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
