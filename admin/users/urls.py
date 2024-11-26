from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView

from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    # path('activate/', views., name='index'),
    path('login/', LoginView.as_view(
        template_name='users/login.html',
        next_page=reverse_lazy('home:index'),
    ), name='login'),

    path('logout/', LogoutView.as_view(
        next_page=reverse_lazy('home:index'),
        template_name='users/logout.html',
    ), name='logout'),
    # path('recover/<std:token>', views., name='index'),
    # path('password_change/', views., name='index'),
    # path('password_change/done/', views., name='index'),

    # path('password_reset/', views., name='index'),
    # path('password_reset/done/', views., name='index'),

]
