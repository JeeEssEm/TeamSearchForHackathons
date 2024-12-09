from django.urls import path

from . import views

app_name = 'wishes'
urlpatterns = [
    path('list/<int:page>', views.WishesListView.as_view(), name='list'),
    path('detail/<int:wid>', views.WishDetailView.as_view(), name='detail'),
]
