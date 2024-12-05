from django.urls import path

from . import views

app_name = 'questionary'

urlpatterns = [
    # path('/<int:q_id>', name='get')
    # path('/list/<int:page>', name='list')
    path('validate/', views.ValidateQuestionaryView.as_view(), name='validate'),
]
