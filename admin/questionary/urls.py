from django.urls import path

from . import views

app_name = 'questionary'

urlpatterns = [
    path('validate-by-id/<int:user_id>/', views.ValidateQuestionaryByIdView.as_view(), name='validate_by_id'),
    path('validate/', views.ValidateQuestionaryView.as_view(), name='validate'),
    path('list/<int:page>', views.QuestionaryListView.as_view(), name='list'),
]
