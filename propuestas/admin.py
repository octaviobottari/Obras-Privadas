from django.contrib import admin
from .models import Usuario, Propuesta

@admin.register(Propuesta)
class PropuestaAdmin(admin.ModelAdmin):
    list_display = ['TITULO', 'PROVINCIA', 'votos_positivos', 'votos_negativos', 'buscando_inversiones', 'llamado_a_licitacion']  # Added 'buscando_inversiones' and 'llamado_a_licitacion'
    list_filter = ['PROVINCIA', 'buscando_inversiones', 'llamado_a_licitacion']  # Added filters for 'buscando_inversiones' and 'llamado_a_licitacion'
    search_fields = ['TITULO', 'IDEA', 'PROVINCIA']

    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            obj.creador = request.user  # Assign current logged-in user as the creator
        obj.save()  # Save the object

admin.site.register(Usuario)