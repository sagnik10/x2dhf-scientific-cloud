from django.contrib import admin
from .models import MolecularSystem,Computation,ComputationParameter
@admin.register(MolecularSystem)
class MolecularSystemAdmin(admin.ModelAdmin):
    list_display=['name','molecule_formula','geometry_type','symmetry','user','created_at']
    list_filter=['geometry_type','symmetry','created_at']
    search_fields=['name','molecule_formula','user__username']
    readonly_fields=['created_at','updated_at']
@admin.register(Computation)
class ComputationAdmin(admin.ModelAdmin):
    list_display=['title','theory','status','user','created_at','cpu_time_seconds']
    list_filter=['theory','status','created_at']
    search_fields=['title','description','user__username']
    readonly_fields=['created_at','updated_at','started_at','completed_at']
@admin.register(ComputationParameter)
class ComputationParameterAdmin(admin.ModelAdmin):
    list_display=['computation','key','value']
    search_fields=['computation__title','key']
