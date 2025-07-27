from django.urls import path
from . import views

urlpatterns = [
    path('', views.hello_world, name='hello_world'),
    path('add-setup/', views.add_setup, name='add_setup'),
    path('filter-setups/', views.filter_setups, name='filter_setups'),
]