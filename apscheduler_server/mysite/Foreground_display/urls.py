from django.conf.urls import url
from Foreground_display import views

urlpatterns = [
    url(r'^login', views.login),
    url(r'^test', views.test),
    url(r'^download_file', views.download_file,name='download_file'),


]
