#!/usr/bin/env python

import os

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View
from webgemdeps.forms import SignInForm
from webgemdeps.models import User
from webgemdeps.utils import get_available_apps


class UserSignIn(View):
    """
    Handle user signin.
    """

    def post(self, request):
        print request.user
        form = SignInForm(request.POST)
        try:
            if form.is_valid():
                input_username = form.cleaned_data['username']
                input_password_raw = form.cleaned_data['password']
                input_password = input_password_raw.encode('utf-8')
                user = authenticate(username=input_username,
                                    password=input_password)
                if user:
                    if user.is_active:
                        request.session['user'] = user.username
                        login(request, user)
                        return HttpResponseRedirect('/home/')
                else:
                    print("Incorrect Username/Password")
                    messages.error(request, "Incorrect Username/Password")
                    raise Exception
            else:
                messages.error(request, "Something went wrong.")
                raise Exception
        except Exception as e:
            print e
            return render(request, 'index.html')


class UserSignOut(View):
    """
    Handle user signin.
    """

    def get(self, request):
        if not request.user.is_authenticated():
            if 'user' in request.session:
                del request.session['user']
        else:
            logout(request)
            if 'user' in request.session:
                del request.session['user']
        return HttpResponseRedirect('/')


class UserHome(View):
    """
    Display user's home.
    """

    def get(self, request):
        if request.user.is_authenticated():
            completed_apps, pending_apps = get_available_apps()
            any_apps = False
            if completed_apps or pending_apps:
                any_apps = True
            return render(request, 'home.html',
                          {'any_apps': any_apps,
                           'completed_apps': completed_apps,
                           'pending_apps': pending_apps})
        else:
            return HttpResponseRedirect('/')
