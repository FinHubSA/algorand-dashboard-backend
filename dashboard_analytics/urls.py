from django.conf.urls import url
from dashboard_analytics import views

urlpatterns = [
    url(r'^api/dashboard$', views.account_list)
    #url(r'^api/tutorials/(?P<pk>[0-9]+)$', views.tutorial_detail),
    #url(r'^api/tutorials/published$', views.tutorial_list_published)
]
