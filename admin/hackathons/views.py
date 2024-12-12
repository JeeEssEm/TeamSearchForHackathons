from asgiref.sync import sync_to_async
from math import ceil

from django.views.generic import View
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect, aget_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User as UserModel

from dependency_injector.wiring import Provide, inject

from hackathons.forms import HackathonForm
from teamsearchadmin.mixins import AsyncLoginRequiredMixin

from core.dependencies.container import Container
from core.services import HackathonsService
from core.dtos import CreateHackathon


class HackathonsListView(AsyncLoginRequiredMixin, View):
    template_name = 'hackathons/list.html'

    @inject
    async def get(self, request, page, db=Provide[Container.db]):
        date = request.GET.get('date')
        sort_start_date = request.GET.get('sort_start_date', 'asc')
        sort_end_date = request.GET.get('sort_end_date', 'asc')
        filters = {
            'date': date,
            'sort_start_date': sort_start_date,
            'sort_end_date': sort_end_date
        }

        async with db.session() as session:
            repo = HackathonsService(session)

            limit = 10
            total, hacks = await repo.get_hacks_list(filters, page, limit)
            last_page = ceil(total / limit)

            return TemplateResponse(
                request,
                self.template_name,
                context={
                    'hacks': hacks,
                    'total': total,
                    'current_page': page,
                    'prev_page': page - 1,
                    'next_page': page + 1 if last_page > page else 0,
                    'last_page': last_page or page,
                    'date': date,
                    'sort_start_date': sort_start_date,
                    'sort_end_date': sort_end_date
                }
            )


class HackathonCreateView(AsyncLoginRequiredMixin, View):
    template_name = 'hackathons/detail.html'

    async def get(self, request):
        form = HackathonForm()
        return TemplateResponse(
            request,
            self.template_name,
            context={'form': form, 'name': 'Создание хакатона'}
        )

    @inject
    async def post(self, request, db=Provide[Container.db]):
        form = HackathonForm(request.POST)
        if not form.is_valid():
            for error in form.errors:
                messages.error(request, form.errors[error].as_data()[0].message)
            return TemplateResponse(
                request,
                self.template_name,
                context={'form': form, 'name': 'Создание нового хакатона'}
            )
        async with db.session() as session:
            repo = HackathonsService(session)
            hack = await repo.create_hackathon(CreateHackathon(
                title=form.cleaned_data['title'],
                start_date=form.cleaned_data['start_date'],
                end_date=form.cleaned_data['end_date'],
                id=-1  # ну а че ещё поделать
            ))
            # TODO: сделать проверку на похожие названия
            link = request.build_absolute_uri(
                reverse_lazy('hackathons:detail', kwargs={'hack_id': hack.id})
            )
            messages.success(
                request,
                f'Вы успешно создали <a href="{link}">хакатон</a>',
                extra_tags='safe'
            )
            return redirect('hackathons:create')


class HackathonDetailView(AsyncLoginRequiredMixin, View):
    template_name = 'hackathons/detail.html'

    @inject
    async def get(self, request, hack_id, db=Provide[Container.db]):
        async with db.session() as session:
            service = HackathonsService(session)
            try:
                hack = await service.get_hack(hack_id)
            except Exception as e:
                messages.error(request, f'Что-то пошло не так... {e}')

            form = HackathonForm(initial={
                'title': hack.title,
                'start_date': str(hack.start_date),
                'end_date': str(hack.end_date),
            })

            return TemplateResponse(
                request,
                self.template_name,
                context={'form': form, 'name': 'Редактирование хакатона'}
            )

    @inject
    async def post(self, request, hack_id, db=Provide[Container.db]):
        form = HackathonForm(request.POST)
        if not form.is_valid():
            return TemplateResponse(
                request,
                self.template_name,
                context={'form': form, 'name': 'Редактирование хакатона'}
            )

        async with db.session() as session:
            service = HackathonsService(session)
            try:
                hack = await service.edit_hack(hack_id, CreateHackathon(
                    id=hack_id,
                    title=form.cleaned_data['title'],
                    start_date=form.cleaned_data['start_date'],
                    end_date=form.cleaned_data['end_date'],
                ))
                link = request.build_absolute_uri(
                    reverse_lazy('hackathons:detail', kwargs={'hack_id': hack.id})
                )
                messages.success(request, f'Вы успешно изменили <a href="{link}">хакатон</a>',
                                 extra_tags='safe')
            except Exception as e:
                messages.error(request, f'Что-то пошло не так... {e}')
        return redirect(reverse_lazy('hackathons:list', kwargs={'page': 1}))
