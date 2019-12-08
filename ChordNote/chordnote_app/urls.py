from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^api/v1/register/$', views.RegisterView.as_view(), name='register'),
    url(r'^api/v1/auth/$', views.AuthView.as_view(), name='auth'),
    url(r'^api/v1/book/$', views.BookView.as_view(), name='book'),
    url(r'^api/v1/chapter/$', views.ChapterView.as_view(), name='chapter'),
    url(r'^api/v1/user_information/$', views.UserInformationView.as_view(), name='user_information'),
    url(r'^api/v1/moment/$', views.MomentView.as_view(), name='moment'),
    url(r'^api/v1/moment_detail/$', views.Moment_DetailView.as_view(), name='moment_detail'),
    url(r'^api/v1/comment_detail/$', views.Comment_DetailView.as_view(), name='comment_detail'),
]

