from django import forms
from django.contrib.auth.models import User


class SignInForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


class NewStatusForm(forms.Form):
    appname = forms.CharField()
    version = forms.CharField()
    gemfile = forms.FileField()
    gemfilelock = forms.FileField()
