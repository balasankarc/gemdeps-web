from django.conf.urls import url
from django.contrib import admin

from webgemdeps.views import StaticPages

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', StaticPages.Index.as_view()),
]
