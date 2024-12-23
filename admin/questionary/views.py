from math import ceil

from django.views.generic import View
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect, aget_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User as UserModel

from dependency_injector.wiring import Provide, inject

from teamsearchadmin.mixins import AsyncLoginRequiredMixin

from core.dependencies.container import Container
from core.services import UsersService
from .forms import QuestionaryForm


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
                return redirect(reverse_lazy('questionary:list', kwargs={'page': 1}))
            try:
                moderator = await aget_object_or_404(UserModel, id=user.moderator_id)
            except Exception as e:
                moderator = None
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
    async def get(self, request, page, db=Provide[Container.db]):
        async with db.session() as session:
            user_service = UsersService(session)
            filters = {}
            status = request.GET.get('status')
            mine = request.GET.get('mine', 'False') == 'True'
            if status:
                filters['status'] = status
            if mine:
                filters['moderator_id'] = request.user.id

            limit = 10
            total, questionaries = await user_service.get_all_short_forms(
                page, filters, limit
            )
            last_page = ceil(total / limit)

            return TemplateResponse(
                request,
                self.template_name,
                context={
                    'questionaries': questionaries,
                    'total': total,
                    'current_page': page,
                    'prev_page': page - 1,
                    'next_page': page + 1 if last_page > page else 0,
                    'last_page': last_page or page,
                    'status': status,
                    'mine': mine
                }
            )
