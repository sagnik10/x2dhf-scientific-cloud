from django.contrib import admin
from .models import ComputationResult,ResultVisualization,Export
@admin.register(ComputationResult)
class ComputationResultAdmin(admin.ModelAdmin):
    list_display=['computation','user','total_energy','created_at']
    list_filter=['created_at']
    search_fields=['computation__title','user__username']
    readonly_fields=['created_at']
@admin.register(ResultVisualization)
class ResultVisualizationAdmin(admin.ModelAdmin):
    list_display=['title','plot_type','result','created_at']
    list_filter=['plot_type','created_at']
    search_fields=['title','result__computation__title']
    readonly_fields=['created_at']
@admin.register(Export)
class ExportAdmin(admin.ModelAdmin):
    list_display=['result','format','user','created_at']
    list_filter=['format','created_at']
    search_fields=['result__computation__title','user__username']
    readonly_fields=['created_at']
