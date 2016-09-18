from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import View


class Index(View):
    """
    Displays general index page.
    """

    def get(self, request):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/home/')
        else:
            return render(request, 'index.html')
