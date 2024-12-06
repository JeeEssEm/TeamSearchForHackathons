from django.urls import path

from . import views

app_name = 'questionary'

urlpatterns = [
    # path('/<int:q_id>', name='get')
    # path('/list/<int:page>', name='list')
    path('validate-by-id/<int:user_id>/', views.ValidateQuestionaryByIdView.as_view(), name='validate_by_id'),
    path('validate/', views.ValidateQuestionaryView.as_view(), name='validate'),
    path('list/', views.QuestionaryListView.as_view(), name='list')
]
