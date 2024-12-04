from django.views.generic import View
from django.template.response import TemplateResponse

from teamsearchadmin.mixins import AsyncLoginRequiredMixin
# from django.forms.

# from core.services import

from .forms import QuestionaryForm
from core.dtos import User


class ValidateQuestionaryView(AsyncLoginRequiredMixin, View):
    template_name = 'questionaries/validate.html'

    async def get(self, request):
        # moderator_id = request.user.id
        # user = await user_service.get_forms(moderator_id)

        mock_user = User(
            id=1,
            name='John',
            surname='Doe',
            middle_name='Иванович',
            roles=['Backend', 'DevOps'],
            technologies=['Docker', 'Kubernetes', 'Django', 'Flask'],
            about_me='Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. ',
            group='БИВТ-24-9',
            uni='МИСиС',
            year_of_study=2
        )
        form = QuestionaryForm()
        return TemplateResponse(
            request,
            template=self.template_name,
            context={
                'form': form,
                'q': mock_user
            })

    async def post(self, request):
        ...
