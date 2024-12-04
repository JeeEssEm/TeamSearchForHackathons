from django.urls import path
from . import views

app_name = "technologies"

urlpatterns = [
    path("create/", views.CreateTechnologyView.as_view(), name="create"),
    path("list/<int:page>", views.TechnologiesListView.as_view(), name="list"),
    path("delete_multiple/", views.TechnologiesDeleteView.as_view(), name="delete"),
    path("edit/<int:tech_id>", views.TechnologiesEditView.as_view(), name="edit"),
    path("delete/<int:tech_id>", views.DeleteTechnologyView.as_view(), name="delete_one"),
]
