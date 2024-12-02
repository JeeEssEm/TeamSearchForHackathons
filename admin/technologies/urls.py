from django.urls import path
from . import views

app_name = "technologies"

urlpatterns = [
    path("create/", views.CreateTechnologyView.as_view(), name="create"),
]
