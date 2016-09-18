from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.views.static import serve

from webgemdeps.views import StaticPages, UserManagement, StatusManagement

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', StaticPages.Index.as_view()),
    url(r'^sign_in/$',
        UserManagement.UserSignIn.as_view()),
    url(r'^sign_out/$',
        UserManagement.UserSignOut.as_view()),
    url(r'^new_status/$',
        StatusManagement.StatusCreate.as_view()),
    url(r'^home/$',
        UserManagement.UserHome.as_view()),
    url(r'^resources/(?P<path>.*)$',
        serve,
        {'document_root': settings.MEDIA_ROOT, }),
]
