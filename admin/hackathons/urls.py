from django.urls import path

from . import views

app_name = 'hackathons'

urlpatterns = [
    path('list/<int:page>', views.HackathonsListView.as_view(), name='list'),
    path('create/', views.HackathonCreateView.as_view(), name='create'),
    path('edit/<int:hack_id>/', views.HackathonDetailView.as_view(), name='detail'),
]
