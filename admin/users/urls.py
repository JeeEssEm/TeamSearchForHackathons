from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetCompleteView,
    PasswordResetConfirmView
)

from .forms import LoginForm
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('activate/', views.ActivateUserView.as_view(), name='activate'),
    path('login/', views.CustomLoginView.as_view(
        next_page=reverse_lazy('home:index'),
        authentication_form=LoginForm,
        redirect_authenticated_user=True
    ), name='login'),
    path('resend_activation_email/', views.ResendActivationEmailView.as_view(),
         name='resend_activation_email'),
    path('logout/', LogoutView.as_view(
        next_page=reverse_lazy('home:index'),
        template_name='users/logout.html',
    ), name='logout'),
    path('password_reset/', PasswordResetView.as_view(
        template_name='users/password_reset.html',
        email_template_name='users/password_reset_email.html',
        success_url=reverse_lazy('users:password_reset_done'),
    ), name='password_reset'),

    path('password_reset/done/', PasswordResetDoneView.as_view(
        template_name='includes/message.html',
        extra_context={
            'title': 'Восстановление',
            'text': 'Письмо с восстановлением отправлено вам на почту'
        },
    ), name='password_reset_done'),

    path('reset/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html',
        success_url=reverse_lazy('users:password_reset_complete'),
    ),
         name='password_reset_confirm'),
    path('reset/done', PasswordResetCompleteView.as_view(
        template_name='includes/message.html',
        extra_context={
            'title': 'Успех',
            'text': 'Пароль успешно изменён'
        }
    ),
         name='password_reset_complete'),
]
