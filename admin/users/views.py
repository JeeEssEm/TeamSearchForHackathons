import jwt
from django.conf import settings
from django.contrib import messages
from django.views.generic import FormView, View
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.core.mail import send_mail

from .models import Invite
from .forms import SignUpForm, ResendActivationForm
from .utils import decode_jwt_token, generate_jwt_token


class SignUpView(FormView):
    template_name = 'users/signup.html'
    model = User
    success_url = reverse_lazy('users:login')
    form_class = SignUpForm

    def dispatch(self, request, *args, **kwargs):
        token = request.GET.get('invite')
        self.token = get_object_or_404(Invite, token=token)
        if self.token.is_used:
            return HttpResponse('Токен уже использован', status=400)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)

        user.is_active = settings.DEFAULT_USER_ACTIVITY
        user.is_staff = self.token.is_superuser
        user.save()

        self.token.is_used = True
        self.token.user = user
        self.token.save()

        if not settings.DEFAULT_USER_ACTIVITY:
            token = generate_jwt_token(user.id)
            link = self.request.build_absolute_uri(
                reverse_lazy('users:activate')
            )[:-1] + f'?token={token}'

            link = f'<a href="{link}">ссылке</a>'
            send_mail(
                'Активация аккаунта',
                # settings.DEFAULT_FROM_EMAIL,
                f'Для активации аккаунта перейдите по {link}',
                'test',
                [form.cleaned_data.get('email')],
            )
            messages.success(
                self.request,
                'Письмо с кодом активации отправлено на вашу почту'
            )

        return super().form_valid(form)


class ActivateUserView(View):
    template_name = 'users/activate.html'

    def get(self, request, *args, **kwargs):
        token = request.GET.get('token')
        try:
            user_id = decode_jwt_token(token).get('user_id')
            user = get_object_or_404(User, id=user_id)
            if user.is_active:
                messages.success(request, 'Аккаунт уже активирован')
            else:
                user.is_active = True
                user.save()
                messages.success(request, 'Аккаунт успешно активирован')
            return render(request, self.template_name)
        except jwt.ExpiredSignatureError:
            messages.error(request, 'Токен устарел')
        except jwt.InvalidTokenError:
            messages.error(request, 'Токен недействителен')


class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def form_invalid(self, form):
        username = form.data.get('username')
        kwargs = {
            'email' if '@' in username else 'username': username,
        }
        try:
            user = User.objects.get(**kwargs)
            if not user.is_active:
                link = reverse_lazy('users:resend_activation_email')
                messages.error(
                    self.request,
                    f'Вы можете отправить письмо с кодом активации '
                    f'повторно, перейдя по этой <a href="{link}">ссылке</a>',
                    extra_tags='safe'
                )
        finally:
            return super().form_invalid(form)


class ResendActivationEmailView(FormView):
    template_name = 'users/email_interact.html'
    form_class = ResendActivationForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                form.add_error('email', 'Этот аккаунт уже активирован')
                return super().form_invalid(form)

        except User.DoesNotExist:
            form.add_error('email', 'Пользователя с таким email не существует!')
            return super().form_invalid(form)
        ...  # отправка письма :))
        messages.success(self.request, 'Письмо с кодом активации '
                                       'отправлено на вашу почту')
        return super().form_valid(form)
