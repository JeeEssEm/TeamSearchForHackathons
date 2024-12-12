from math import ceil

from django.shortcuts import redirect, aget_object_or_404
from django.views.generic import View
from django.template.response import TemplateResponse
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.models import User

from dependency_injector.wiring import Provide, inject

from core.repositories import WishesRepository
from core.dependencies.container import Container
from teamsearchadmin.mixins import AsyncLoginRequiredMixin


class WishesListView(AsyncLoginRequiredMixin, View):
    template_name = 'wishes/list.html'

    @inject
    async def get(self, request, page, db=Provide[Container.db]):
        is_archived = request.GET.get('is_archived', False) == 'True'
        limit = 10
        async with db.session() as session:
            repo = WishesRepository(session)
            total, wishes = await repo.get_wishes(page, limit, is_archived)
            last_page = ceil(total / limit)

        return TemplateResponse(request, self.template_name, {
            'wishes': wishes,
            'total': total,
            'current_page': page,
            'prev_page': page - 1,
            'next_page': page + 1 if last_page > page else 0,
            'last_page': last_page or page,
            'is_archived': is_archived
        })


class WishDetailView(AsyncLoginRequiredMixin, View):
    template_name = 'wishes/detail.html'

    @inject
    async def get(self, request, wid, db=Provide[Container.db]):
        async with db.session() as session:
            repo = WishesRepository(session)
            moderator = None
            try:
                wish = await repo.get_by_id(wid)
            except Exception as e:
                messages.error(request, f'Что-то пошло не так... {e}')
                return redirect(reverse_lazy('wishes:list', kwargs={'page': 1}))
            if wish.is_archived:
                moderator = await aget_object_or_404(User, id=wish.moderator_id)

            return TemplateResponse(request, self.template_name, {
                'wish': wish,
                'moderator': moderator,
            })

    @inject
    async def post(self, request, wid, db=Provide[Container.db]):
        async with db.session() as session:
            repo = WishesRepository(session)
            await repo.move_to_archive(wid, request.user.id)
            link = request.build_absolute_uri(
                reverse_lazy('wishes:detail', kwargs={'wid': wid})
            )
            messages.success(
                request,
                f'<a href="{link}">Фидбек</a> отправлен в архив',
                extra_tags='safe')
            return redirect(reverse_lazy('wishes:list', kwargs={'page': 1}))
