from asgiref.sync import sync_to_async

from django.views.generic import View
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User as UserModel

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


class ValidateQuestionaryByIdView(AsyncLoginRequiredMixin, View):
    template_name = 'questionaries/validate.html'

    @inject
    async def get(self, request, user_id, db=Provide[Container.db]):
        async with db.session() as session:
            user_service = UsersService(session)
            try:
                user = await user_service.get_form_by_id(user_id)
            except Exception as e:
                messages.error(request, f'Что-то пошло не так... {e}')
                return redirect(reverse_lazy('home:index'))  # TODO: добавить отображание messages
            moderator = await sync_to_async(get_object_or_404)(UserModel, id=user.moderator_id)
            form = QuestionaryForm(initial={'feedback': user.moderator_feedback})
            return TemplateResponse(
                request,
                template=self.template_name,
                context={
                    'form': form,
                    'q': user,
                    'moderator': moderator
                })

    @inject
    async def post(self, request, user_id, db=Provide[Container.db]):
        moderator_id = request.user.id
        form = QuestionaryForm(request.POST)

        async with db.session() as session:
            user_service = UsersService(session)
            form.is_valid()
            feedback = form.cleaned_data.get('feedback')
            link = request.build_absolute_uri(reverse_lazy('questionary:validate_by_id', kwargs={'user_id': user_id}))

            if 'approve' in request.POST:
                await user_service.approve_user(user_id, moderator_id, feedback)
                messages.success(request, f'Вы одобрили анкету <a href="{link}">пользователя</a>', extra_tags='safe')
            elif 'reject' in request.POST:
                await user_service.reject_user(user_id, moderator_id, feedback)
                messages.error(request, f'Вы отклонили анкету <a href="{link}">пользователя</a>', extra_tags='safe')
            # отобразить message со ссылкой на то, что ты наделал с
            # предыдущим юзером. Например, случайно реджектнул

        return redirect(reverse_lazy('questionary:validate'))


class QuestionaryListView(AsyncLoginRequiredMixin, View):
    template_name = 'questionaries/list.html'

    @inject
    async def get(self, request, db=Provide[Container.db]):
        async with db.session() as session:
            user_service = UsersService(session)
            questionaries = await user_service.get_all_short_forms()

            return TemplateResponse(
                request,
                self.template_name,
                context={
                    'questionaries': questionaries 
                }
            )
