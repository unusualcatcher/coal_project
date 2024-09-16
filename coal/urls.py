from .views import dashboard, home, visme, form
from django.urls import path

urlpatterns = [
    path('', home, name='home'),
    path('visme/', visme, name='visme'),
    path('dashboard/', dashboard, name='dashboard'),
    path('form/', form, name='form'),
]