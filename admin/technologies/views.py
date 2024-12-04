from math import ceil
from json import dumps, loads

from asgiref.sync import sync_to_async

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View
from django.contrib import messages
from django.template.response import TemplateResponse

from dependency_injector.wiring import Provide, inject

from core.dependencies.container import Container
from core.repositories import TechnologiesRepository
from .forms import CreateTechnologyForm

from teamsearchadmin.mixins import AsyncLoginRequiredMixin


class CreateTechnologyView(AsyncLoginRequiredMixin, View):
    template_name = 'technologies/create.html'

    @inject
    async def post(self, request, db=Provide[Container.db]):
        form = CreateTechnologyForm(request.POST)
        if form.is_valid():
            async with db.session() as session:
                tech_repo = TechnologiesRepository(session)
                # какая-нибудь проверка на похожие названия
                try:
                    title = form.cleaned_data.get("title")
                    await tech_repo.create(title)
                    messages.success(
                        self.request,
                        f"Новая технология {title} создана!"
                    )
                except Exception as e:
                    await db.init_models()  # пока что затычка...
                    messages.error(self.request, f"Что-то пошло не так: {e}")

        return TemplateResponse(self.request, self.template_name, {
            'form': form
        })

    async def get(self, request):
        form = CreateTechnologyForm()
        return TemplateResponse(
            request, self.template_name,
            {
                'form': form
            })


class TechnologiesListView(AsyncLoginRequiredMixin, View):
    template_name = 'technologies/list.html'

    @inject
    async def get(self, request, page=1, db=Provide[Container.db]):
        async with db.session() as session:
            tech_service = TechnologiesRepository(session)
            limit = 1
            total, technologies = await tech_service.get_technologies(limit, page)
            last_page = ceil(total / limit)

            return TemplateResponse(self.request, self.template_name, {
                'technologies': technologies,
                'total': total,
                'current_page': page,
                'prev_page': page - 1,
                'next_page': page + 1 if last_page > page else 0,
                'last_page': last_page or page
            })

    async def post(self, request, page):
        selected = request.POST.getlist('selected_technologies')
        if selected:
            return redirect(
                reverse_lazy('technologies:delete')
                + f'?selected_technologies={dumps(selected)}')

        messages.error(
            request,
            "Вы не выбрали ни одной технологии для удаления"
        )
        return await self.get(request)


class TechnologiesDeleteView(AsyncLoginRequiredMixin, View):
    template_name = 'technologies/delete.html'

    @inject
    async def get(self, request, db=Provide[Container.db]):
        selected = loads(request.GET.get('selected_technologies', '[]'))
        selected = list(map(int, selected))
        if not selected:
            return redirect(reverse_lazy('technologies:list'))
        async with db.session() as session:
            tech_repo = TechnologiesRepository(session)
            techs = await tech_repo.get_technologies_by_id(selected)

            await sync_to_async(request.session.__setitem__)(
                'selected_technologies', list(map(lambda t: t.__dict__, techs))
            )

            return TemplateResponse(request, self.template_name, {
                'technologies': techs
            })

    @inject
    async def post(self, request, db=Provide[Container.db]):
        selected = await sync_to_async(request.session.get)(
            'selected_technologies'
        )
        ids = []
        titles = []
        for t in selected:
            titles.append(t['title'])
            ids.append(t['id'])

        async with db.session() as session:
            tech_repo = TechnologiesRepository(session)
            try:
                await tech_repo.delete_technologies_by_id(ids)
                messages.success(
                    request,
                    f"Выбранные технологии успешно удалены:"
                    f" {', '.join(titles)}"
                )
            except Exception as e:
                messages.error(request, f'Что-то пошло не так: {e}')
        return redirect(reverse_lazy('technologies:list', kwargs={'page': 1}))


class TechnologiesEditView(AsyncLoginRequiredMixin, View):
    template_name = 'technologies/edit.html'

    @inject
    async def get(self, request, tech_id, db=Provide[Container.db]):
        async with db.session() as session:
            tech_repo = TechnologiesRepository(session)
            try:
                tech = await tech_repo.get_by_id(tech_id)
                form = CreateTechnologyForm(initial={'title': tech.title})
                
                return TemplateResponse(self.request, self.template_name, {
                    'form': form,
                    'tech': tech
                })
            except Exception as e:
                messages.error(request, f'Что-то пошло не так: {e}')
                return redirect(reverse_lazy('technologies:list', kwargs={'page': 1}))

    @inject
    async def post(self, request, tech_id, db=Provide[Container.db]):
        form = CreateTechnologyForm(request.POST)

        async with db.session() as session:
            tech_repo = TechnologiesRepository(session)
            try:
                form.is_valid()
                title = form.cleaned_data.get('title')
                if not title or not title.strip():
                    raise ValueError("Поле не может состоять из пробелов!")
                if 'delete' in request.POST:
                    await tech_repo.delete_technologies_by_id([tech_id])
                    messages.success(
                        request,
                        f'Технология <{title}> успешно удалена'
                    )
                elif 'save' in request.POST:
                    await tech_repo.edit(tech_id, title)
                    messages.success(
                        request,
                        f'Технология успешно изменена: <{title}>'
                    )

            except Exception as e:
                messages.error(request, f'Что-то пошло не так: {e}')
            return redirect(reverse_lazy('technologies:list', kwargs={'page': 1}))
