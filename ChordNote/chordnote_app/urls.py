from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^api/v1/register/$', views.RegisterView.as_view(), name='register'),
    url(r'^api/v1/auth/$', views.AuthView.as_view(), name='auth'),
    url(r'^api/v1/book/all$', views.BookView.as_view(), name='book'),
    url(r'^api/v1/book/chapter/all$', views.Chapter_Info_View.as_view(), name='chapter'),
    url(r'^api/v1/user_information/$', views.UserInformationView.as_view(), name='user_information'),
    url(r'^api/v1/moment/$', views.MomentView.as_view(), name='moment'),
    url(r'^api/v1/moment_detail/$', views.Moment_DetailView.as_view(), name='moment_detail'),
    url(r'^api/v1/comment_detail/$', views.Comment_DetailView.as_view(), name='comment_detail'),
    url(r'^api/v1/book/period$', views.PeriodView.as_view(), name='period'),
    url(r'^api/v1/book/period/question$', views.QuestionView.as_view(), name='question'),
    url(r'^api/v1/book/period/comment$', views.Comment_Commen_View.as_view(), name='comment_common'),
    url(r'^api/v1/book/period/comment/collect$', views.Comment_Collect_View.as_view(), name='comment_common'),
]
