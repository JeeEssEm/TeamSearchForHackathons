from django.shortcuts import render
from django.views.generic import FormView, View
from django.contrib import messages
from django.template.response import TemplateResponse

from dependency_injector.wiring import Provide, inject

from core.dependencies.container import Container
from core.repositories import TechnologiesRepository
from .forms import CreateTechnologyForm


class CreateTechnologyView(View):
    template_name = 'technologies/create.html'

    @inject
    async def post(self, request, db=Provide[Container.db]):
        form = CreateTechnologyForm(request.POST)
        if form.is_valid():
            async with db.session() as session:
                tech_service = TechnologiesRepository(session)
                try:
                    await tech_service.create(
                        form.cleaned_data.get("title"))
                    messages.success(self.request, "Новая технология создана")
                except Exception as e:
                    # await db.init_models()
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
