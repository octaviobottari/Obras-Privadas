# obras_privadas/main/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/ciudadano/', views.register_ciudadano, name='register_ciudadano'),
    path('register/empresa/', views.register_empresa, name='register_empresa'),
    path('propuestas/', views.propuesta_list, name='propuesta_list'),
    path('propuestas/<int:pk>/', views.propuesta_detail, name='propuesta_detail'),
    path('propuestas/new/', views.propuesta_create, name='propuesta_create'),
]
