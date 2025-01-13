from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from propuestas import views as propuestas_views
from django.contrib.auth.views import LoginView, LogoutView
from propuestas.views import rate_propuesta, propuestas_inversiones, profile, PropuestaDetailView, financiar_propuesta, llamado_a_licitacion

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', propuestas_views.register, name='register'),
    path('register/comun/', propuestas_views.register_comun, name='register_comun'),
    path('register/empresa/', propuestas_views.register_empresa, name='register_empresa'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('proponer/', propuestas_views.proponer, name='proponer'),
    path('propuestas/', propuestas_views.propuestas, name='propuestas'),
    path('propuestas/<int:propuesta_id>/rate/', propuestas_views.rate_propuesta, name='rate_propuesta'),
    path('', propuestas_views.index, name='index'),
    path('propuestas_inversiones/', propuestas_views.propuestas_inversiones, name='propuestas_inversiones'),
    path('propuesta/<int:pk>/', propuestas_views.propuesta_detail, name='propuesta_detail'),
    path('propuesta/<int:propuesta_id>/financiar/', propuestas_views.financiar_propuesta, name='financiar_propuesta'),
    path('llamado-a-licitacion/', propuestas_views.llamado_a_licitacion, name='llamado_a_licitacion'),
    path('profile/', propuestas_views.profile, name='profile'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
