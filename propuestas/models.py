from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_delete
import os
from django.utils import timezone
from django.conf import settings


class Usuario(AbstractUser):
    nombre = models.CharField(max_length=30)
    apellido = models.CharField(max_length=30)
    fecha_de_nacimiento = models.DateField(blank=True, null=True)
    provincia = models.CharField(max_length=30)
    dni = models.CharField(max_length=10)
    tipo_usuario = models.CharField(max_length=20, choices=[
        ('comun', 'Común'),
        ('empresa', 'Empresa')
    ])

    # Campos adicionales para usuario empresa
    nombre_empresa = models.CharField(max_length=100, blank=True, null=True)
    cuit_empresa = models.CharField(max_length=20, blank=True, null=True)
    foreign_company = models.BooleanField(default=False)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    propuestas_financiadas = models.ManyToManyField('Propuesta', related_name='empresas_que_financiaron', blank=True)


    groups = models.ManyToManyField(
        'auth.Group',
        related_name='user_set_usuario',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='user_set_usuario',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return f"{self.username} ({self.nombre} {self.apellido})"

class Propuesta(models.Model):
    TITULO = models.CharField(max_length=255)
    FOTO_DE_PERFIL_DEL_PROYECTO = models.ImageField(upload_to='images/', blank=True, null=True)
    IDEA = models.TextField()
    PROVINCIA = models.CharField(max_length=30)
    PROPUESTA_PDF = models.FileField(upload_to='pdfs/', blank=True, null=True)
    votos_positivos = models.PositiveIntegerField(default=0)
    votos_negativos = models.PositiveIntegerField(default=0)
    usuarios_que_han_rateado = models.ManyToManyField(Usuario, related_name='propuestas_rateadas', blank=True)
    buscando_inversiones = models.BooleanField(default=False)
    creador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='propuestas_creadas')
    FORMULARIO_FINANCIAMIENTO = models.FileField(upload_to='formularios/', blank=True, null=True)
    empresas_que_financian = models.ManyToManyField(Usuario, related_name='empresas_financiadoras', blank=True)
    llamado_a_licitacion = models.BooleanField(default=False)


    def __str__(self):
        return self.TITULO
    
class Comment(models.Model):
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    propuesta = models.ForeignKey(Propuesta, on_delete=models.CASCADE)
    comment = models.TextField()  # Ensure this field exists
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.comment} {self.created_at}"

@receiver(post_delete, sender=Propuesta)
def delete_propuesta_files(sender, instance, **kwargs):
    # Delete the associated image file if it exists
    if instance.FOTO_DE_PERFIL_DEL_PROYECTO:
        if os.path.isfile(instance.FOTO_DE_PERFIL_DEL_PROYECTO.path):
            os.remove(instance.FOTO_DE_PERFIL_DEL_PROYECTO.path)
    # Delete the associated PDF file if it exists
    if instance.PROPUESTA_PDF:
        if os.path.isfile(instance.PROPUESTA_PDF.path):
            os.remove(instance.PROPUESTA_PDF.path)
