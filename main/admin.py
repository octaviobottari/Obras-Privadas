# main/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Ciudadano

admin.site.register(Ciudadano, UserAdmin)
