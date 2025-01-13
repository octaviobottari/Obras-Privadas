# main/models.py

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class Ciudadano(AbstractUser):
    fecha_nacimiento = models.DateField(null=True, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    municipio = models.CharField(max_length=100, blank=True)
    dni = models.CharField(max_length=20, unique=True, blank=True)

    # Specify related_name to resolve E304 error
    groups = models.ManyToManyField(Group, related_name='ciudadano_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='ciudadano_permissions', blank=True)

    def __str__(self):
        return self.username
