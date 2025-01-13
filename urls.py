# ObrasPrivadas/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('register_user.urls')),  # Include your app's urls here
    # Add more paths as needed
]
