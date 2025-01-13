from django.urls import path, include
from. import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('proposals/', views.proposals, name='proposals'),
    path('create_proposal/', views.create_proposal, name='create_proposal'),
    path('proposal/<pk>/', views.proposal_detail, name='proposal_detail'),
    path('vote/<pk>/', views.vote, name='vote'),
    path('propuestas/', include('propuestas.urls')),
    # Add other URL patterns here
    path('accounts/', include('django.contrib.auth.urls')),  # For login, logout, password management
]
