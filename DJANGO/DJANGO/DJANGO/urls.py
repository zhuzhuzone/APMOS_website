"""DJANGO URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from APMOS_WEB.views import Index, Login, FindFeedcode, UpdateAPMOS, UpdateResult, FindAVGPrice, FindPriceVolume, \
    BBticker2Apcode, ApmosSearch, AboutWebsite
from django.views.static import serve

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^index/', Index, name='index'),
    url(r'^login/', Login, name='login'),
    url(r'^FindFeedcode/', FindFeedcode, name='FindFeedcode'),
    url(r'^UpdateAPMOS/', UpdateAPMOS, name='UpdateAPMOS'),
    url(r'UpdateResult/', UpdateResult, name='UpdateResult'),
    url(r'FindAVGPrice/', FindAVGPrice, name='FindAVGPrice'),
    url(r'FindPriceVolume/', FindPriceVolume, name='FindPriceVolume'),
    url(r'BBticker2Apcode/', BBticker2Apcode, name='BBticker2Apcode'),
    url(r'ApmosSearch/', ApmosSearch, name='ApmosSearch'),
    url(r'AboutWebsite/', AboutWebsite, name='AboutWebsite'),
    url(r'^templates/(?P<path>.*)$', serve, {'document_root': 'templates/'})
]
