from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import AccessMixin

from asgiref.sync import sync_to_async


class AsyncLoginRequiredMixin(AccessMixin):
    redirect_field_name = 'next'

    async def dispatch(self, request, *args, **kwargs):
        if not await sync_to_async(lambda: request.user.is_authenticated)():
            return redirect(reverse_lazy('users:login'))
        return await super().dispatch(request, *args, **kwargs)
