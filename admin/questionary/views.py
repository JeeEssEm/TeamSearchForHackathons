from django.views.generic import View
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect

from dependency_injector.wiring import Provide, inject

from teamsearchadmin.mixins import AsyncLoginRequiredMixin
# from django.forms.

# from core.services import
from core.dependencies.container import Container
from core.services import UsersService
from .forms import QuestionaryForm
from core.dtos import User


class ValidateQuestionaryView(AsyncLoginRequiredMixin, View):
    template_name = 'questionaries/validate.html'

    @inject
    async def get(self, request, db=Provide[Container.db]):
        moderator_id = request.user.id
        async with db.session() as session:
            user_service = UsersService(session)
            user = await user_service.get_form(moderator_id)
            form = QuestionaryForm()
            return TemplateResponse(
                request,
                template=self.template_name,
                context={
                    'form': form,
                    'q': user
                })

    @inject
    async def post(self, request, db=Provide[Container.db]):
        moderator_id = request.user.id
        form = QuestionaryForm(request.POST)

        async with db.session() as session:
            user_service = UsersService(session)
            form.is_valid()

            if 'approve' in request.POST:
                ...
            elif 'reject' in request.POST:
                ...
            # отобразить message со ссылкой на то, что ты наделал с
            # предыдущим юзером. Например, случайно реджектнул

        return redirect(reverse_lazy('questionaries:validate'))
