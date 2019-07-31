from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^api/v1/register/$', views.RegisterView.as_view(), name='register'),
    url(r'^api/v1/auth/$', views.AuthView.as_view(), name='auth'),

]

