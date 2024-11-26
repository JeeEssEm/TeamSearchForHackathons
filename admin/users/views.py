from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.conf import settings
from django.views.generic import FormView, CreateView, View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.http import HttpResponse

from .models import Invite


class SignUpView(FormView):
    template_name = 'users/signup.html'
    model = User
    success_url = reverse_lazy('users:login')
    form_class = UserCreationForm

    def dispatch(self, request, *args, **kwargs):
        token = kwargs.get('token')
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
            ...  # send email

        return super().form_valid(form)