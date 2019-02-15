"""transfers URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
from django.urls import path
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static

from sharing.views import OpenView, AddView, AddLink, AddFile
from sharing import api  #import Open, AddLink

urlpatterns = [
    path('admin/', admin.site.urls),
    path('add/', AddView.as_view()),
    path('add/link/', AddLink.as_view()),
    path('add/file/', AddFile.as_view()),
    path('login/', auth_views.LoginView.as_view(template_name='login.html')),
    path('logout/', auth_views.LogoutView.as_view()),
    path('open/<slug:url>/', OpenView.as_view(), name='open'),
    url(r'^api-auth/', include('rest_framework.urls')),
    path('api/open/<slug:url>/', api.Open.as_view(), name='api-open'),
    path('api/add/link/', api.AddLink.as_view()),
    path('api/add/file/', api.AddFile.as_view()),
    path('api/stats/', api.Stats.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
